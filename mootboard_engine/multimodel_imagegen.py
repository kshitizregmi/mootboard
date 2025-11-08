import os
import base64
from io import BytesIO
from PIL import Image
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pydantic import BaseModel
import time

IMAGE_OUPUT_PATH = "output_image/"

class ImageClassification(BaseModel):
    is_sketch: bool

def load_api_key():
    load_dotenv()
    return os.getenv("GOOGLE_API_KEY")

def encode_image(image_data):
    return base64.b64encode(image_data).decode("utf-8")

def save_image(response, path):
    for part in response.parts:
        if image := part.as_image():
            image.save(path)
            return True
    return False

def classify_image(client, image_data):
    prompt = "Is this a sketch or a photo of a person? Respond with 'sketch' or 'person'."
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt, {"inline_data": {"mime_type": "image/png", "data": image_data}}]
    )
    return ImageClassification(is_sketch=response.parts[0].text.lower() == "sketch")

def validate_sketch(client, image_data):
    prompt = "Is this a clear, detailed sketch of a dress with distinct patterns and structure? Respond with 'clear' or 'unclear'."
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt, {"inline_data": {"mime_type": "image/png", "data": image_data}}]
    )
    return response.parts[0].text.lower() == "clear"

def rewrite_prompt(client, original_prompt, base_image_data=None, face_image_data=None):
    rewrite_instruction = (
        "Rewrite this prompt to generate a high-quality, consistent image while strictly preserving the exact design of the input sketch. "
        "The model must wear the dress from the sketch, maintaining all its patterns, shapes, colors, and structural details without any modifications. "
        "Include details for soft natural lighting, a fashion runway background with elegant ambiance, confident model pose (walking), and seamless, realistic face integration if provided. "
        "Ensure photorealistic output with vibrant colors and sharp details. The Image should not look cartoonish. Use face image provided and blend it with dress. Original prompt: '{}'"
    ).format(original_prompt)
    
    contents = [rewrite_instruction]
    if base_image_data:
        contents.append({"inline_data": {"mime_type": "image/png", "data": base_image_data}})
    if face_image_data:
        contents.append({"inline_data": {"mime_type": "image/png", "data": face_image_data}})
    
    response = client.models.generate_content(model="gemini-2.5-flash", contents=contents)
    rewritten_prompt = response.parts[0].text
    print(f"Rewritten Prompt: {rewritten_prompt}")
    return rewritten_prompt

def generate_image(client, model_id, text_prompt, base_image_data, face_image_data_list=None, max_retries=3):
    output_paths = []
    sketches = [base_image_data] if base_image_data else []
    
    for i, sketch in enumerate(sketches):
        if not validate_sketch(client, sketch):
            print(f"Sketch {i} is unclear, using original prompt to avoid misalignment.")
            contents = [text_prompt, {"inline_data": {"mime_type": "image/png", "data": sketch}}]
        else:
            for attempt in range(max_retries):
                try:
                    rewritten_prompt = rewrite_prompt(client, text_prompt, sketch)
                    contents = [rewritten_prompt, {"inline_data": {"mime_type": "image/png", "data": sketch}}]
                    response = client.models.generate_content(model=model_id, contents=contents)
                    path = os.path.join(IMAGE_OUPUT_PATH, f'output_{i}.png')
                    if save_image(response, path):
                        output_paths.append(path)
                        break
                    else:
                        print(f"Attempt {attempt + 1} failed for sketch {i}. Retrying...")
                        time.sleep(1)
                except Exception as e:
                    print(f"Error in attempt {attempt + 1} for sketch {i}: {e}")
                    if attempt == max_retries - 1:
                        print(f"Using original prompt as fallback for sketch {i}.")
                        contents = [text_prompt, {"inline_data": {"mime_type": "image/png", "data": sketch}}]
                        response = client.models.generate_content(model=model_id, contents=contents)
                        path = os.path.join(IMAGE_OUPUT_PATH, f'output_{i}_fallback.png')
                        if save_image(response, path):
                            output_paths.append(path)
                    time.sleep(1)
    
    for i, sketch in enumerate(sketches or [None]):
        for j, face_data in enumerate(face_image_data_list or []):
            if sketch and not validate_sketch(client, sketch):
                print(f"Sketch {i} is unclear, using original prompt for face {j}.")
                contents = [text_prompt]
                if sketch:
                    contents.append({"inline_data": {"mime_type": "image/png", "data": sketch}})
                contents.append({"inline_data": {"mime_type": "image/png", "data": face_data}})
            else:
                for attempt in range(max_retries):
                    try:
                        rewritten_prompt = rewrite_prompt(client, text_prompt, sketch, face_data)
                        contents = [rewritten_prompt]
                        if sketch:
                            contents.append({"inline_data": {"mime_type": "image/png", "data": sketch}})
                        contents.append({"inline_data": {"mime_type": "image/png", "data": face_data}})
                        response = client.models.generate_content(model=model_id, contents=contents)
                        path = os.path.join(IMAGE_OUPUT_PATH, f'output_{i}_{j}.png')
                        if save_image(response, path):
                            output_paths.append(path)
                            break
                        else:
                            print(f"Attempt {attempt + 1} failed for sketch {i}, face {j}. Retrying...")
                            time.sleep(1)
                    except Exception as e:
                        print(f"Error in attempt {attempt + 1} for sketch {i}, face {j}: {e}")
                        if attempt == max_retries - 1:
                            print(f"Using original prompt as fallback for sketch {i}, face {j}.")
                            contents = [text_prompt]
                            if sketch:
                                contents.append({"inline_data": {"mime_type": "image/png", "data": sketch}})
                            contents.append({"inline_data": {"mime_type": "image/png", "data": face_data}})
                            response = client.models.generate_content(model=model_id, contents=contents)
                            path = os.path.join(IMAGE_OUPUT_PATH, f'output_{i}_{j}_fallback.png')
                            if save_image(response, path):
                                output_paths.append(path)
                        time.sleep(1)
    
    return output_paths

def validate_image(image_data):
    try:
        Image.open(BytesIO(image_data)).verify()
        return True
    except:
        return False

def process_api_images(image_data_list, text_prompt=None):
    api_key = load_api_key()
    if not api_key:
        raise ValueError("API key not found in .env file")
    
    client = genai.Client(api_key=api_key)
    model_id = "gemini-2.5-flash-image"
    # model_id = "imagen-4.0-generate-001"
    
    sketches = []
    faces = []
    
    for image_data in image_data_list:
        if not validate_image(image_data):
            print("Invalid image data, skipping...")
            continue
        encoded = encode_image(image_data)
        classification = classify_image(client, encoded)
        if classification.is_sketch:
            sketches.append(encoded)
        else:
            faces.append(encoded)
    
    output_paths = []
    
    if not sketches and faces:
        output_paths.extend(generate_image(client, model_id, text_prompt, None, faces))
    else:
        for sketch in sketches:
            output_paths.extend(generate_image(client, model_id, text_prompt, sketch, faces))
    
    for path in output_paths:
        with Image.open(path) as img:
            img.show()
    
    return output_paths

def test_all_inputs(text_prompt):
    test_cases = [
        {'name': 'sketch_face', 'files': ['image_samples/indian_dress.png', 'image_samples/aish.jpg']},
    ]

    for test_case in test_cases:
        print(f"\nRunning test: {test_case['name']}")
        image_data_list = []
        
        for file in test_case['files']:
            try:
                with open(file, 'rb') as f:
                    image_data_list.append(f.read())
            except FileNotFoundError:
                print(f"File {file} not found, skipping...")
                continue
        
        if image_data_list or test_case['name'] == 'empty':
            output_paths = process_api_images(image_data_list, text_prompt)
            print(f"Generated outputs: {output_paths}")
        else:
            print("No valid images provided for this test case.")

if __name__ == "__main__":
    os.makedirs(IMAGE_OUPUT_PATH, exist_ok=True)
    text_prompt = 'Design a mootboard collage Use parts of dress sidewise and add model in middle. using the given sketch, use provided face if available, on different color. Show how it looks in fasion show.'
    test_all_inputs(text_prompt)