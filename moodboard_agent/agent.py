import os, base64
from io import BytesIO
from PIL import Image
from google import genai
from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
import io
from google.genai import types
TEXT_MODEL_ID = "gemini-2.5-flash"
IMAGE_MODEL_ID = "gemini-2.5-flash-image"

def rephrase_prompt(prompt):
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    rephrase_instruction = "Rephrase the following prompt for clarity and specificity, maintaining the original intent: " + prompt + "Do not duplicate any items. Donot add unnecessay information. Be thoughtful while generating mootboard."
    response = client.models.generate_content(
        model=TEXT_MODEL_ID,
        contents=[rephrase_instruction]
    )
    for part in response.parts:
        if part.text:
            return part.text
    return prompt

def _image_from_response(response) -> Image.Image:
    """Extract a PIL.Image from a model response."""
    for part in response.parts:
        as_img = getattr(part, "as_image", None)
        if callable(as_img):
            return as_img()
    raise ValueError("No image found in the tool's response.")

async def create_fashion_moodboard(
    tool_context: ToolContext,
    prompt: str = "",
    input_image_path: str = "",   # optional now
) :
    """
    Generates a fashion moodboard image and, if return_inline=True,
    returns a Markdown snippet that displays it directly in the ADK web UI.
    Optionally also saves to `output_path` if provided.
    """

    output_path: str = "output/moodboard/generated_moodboard.png"
    # print(f"input_prompt: {prompt}, input_image_path: {input_image_path}, output_path: {output_path}")
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        # if not api_key:
        #     return "Error: GOOGLE_API_KEY not found in environment."

        # if not os.path.exists(input_image_path):
        #     return f"Error: Image not found at {input_image_path}"

        client = genai.Client(api_key=api_key)

        # rephrased_prompt = rephrase_prompt(input_prompt)
        image = Image.open(input_image_path)
        prompt = prompt
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt, image],
        )
        # img = _image_from_response(response)
        for part in response.parts:
            print("Saving moodboard image......")
            print(part)
            if part.inline_data is not None:
                print("Saving moodboard image......")
                result_image = part.as_image()
                result_image.save(output_path)
                image = Image.open(output_path)
                image_bytes_io = io.BytesIO()
                image.save(image_bytes_io, format="PNG")
                image_bytes = image_bytes_io.getvalue()
                image_artifact = types.Part.from_bytes(data=image_bytes, mime_type='image/png')
                filename = "moodboard.png"
                await tool_context.save_artifact(filename, image_artifact)

                return {
                    "output_path": output_path,
                    "message": f"Generated image saved to {output_path}"
                }
        # 3) Optional: save to disk
        # saved_note = ""
        # if output_path:
        #     os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        #     img.save(output_path)
        #     saved_note = f"\n\nSaved to: `{os.path.abspath(output_path)}`"

        # if tool_context:
        #     image = Image.open(output_path)
        #     image_bytes_io = io.BytesIO()
        #     image.save(image_bytes_io, format="PNG")
        #     image_bytes = image_bytes_io.getvalue()
        #     image_artifact = types.Part.from_bytes(data=image_bytes, mime_type='image/png')
        #     filename = "moodboard.png"
        #     await tool_context.save_artifact(filename, image_artifact)
        # fallback text if not returning inline
        # return f"Moodboard created successfully.{saved_note}"

    except Exception as e:
        print(f"--- TOOL: EXECUTION FAILED: {e} ---")
        return f"Error during moodboard creation: {e}"

# --- ADK Agent ---
root_agent = LlmAgent(
    name="fashion_moodboard_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You are a helpful fashion design assistant. "
        "You create moodboards when asked. "
        "You always generate model full dress based on sketch. It should always have face."
    ),
    tools=[create_fashion_moodboard]
)