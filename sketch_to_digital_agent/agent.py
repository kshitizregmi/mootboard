from google import genai
from google.genai import types
from google.adk.agents import Agent
from PIL import Image
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def sketch_to_digital(
    image_path: str,
    prompt: str = "Convert the given sketch to a digital illustration with vibrant colors and detailed shading.",
    output_path: str = "output/sketch-to-digital/generated_image2.png",
):
    """
    Converts a sketch to a detailed digital illustration using Gemini.

    Args:
        image_path (str): Path to the input sketch image.
        prompt (str, optional): Description of desired transformation. Defaults to a vivid digital rendering prompt.
        output_path (str, optional): Path to save the generated image. Defaults to 'generated_image.png'.

    Returns:
        dict: { "output_path": str, "message": str }
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    client = genai.Client(api_key=api_key)

    # Load the input sketch
    image = Image.open(image_path)

    # Generate digital illustration
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt, image],
    )

    # Process the result
    for part in response.parts:
        if part.inline_data is not None:
            result_image = part.as_image()
            result_image.save(output_path)
            return {
                "output_path": output_path,
                "message": f"Generated image saved to {output_path}",
            }

    return {"message": "No image data returned by the model."}


root_agent = Agent(
    name="sketch_to_digital_agent",
    model="gemini-2.5-flash",
    description=(
        "Agent that converts sketches to digital illustrations using Gemini models."
    ),
    instruction=(
        "You are a helpful agent who can convert sketches to digital illustrations."
    ),
    tools=[sketch_to_digital],
)

