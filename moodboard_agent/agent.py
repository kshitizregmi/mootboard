import os, base64
from io import BytesIO
from PIL import Image
from google import genai
from google.adk.agents import LlmAgent

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

def create_fashion_moodboard(
    input_prompt: str,
    input_image_path: str,
    output_path: str = "output/moodboard/generated_moodboard.png",   # optional now
) -> str:
    """
    Generates a fashion moodboard image and, if return_inline=True,
    returns a Markdown snippet that displays it directly in the ADK web UI.
    Optionally also saves to `output_path` if provided.
    """
    print(f"input_prompt: {input_prompt}, input_image_path: {input_image_path}, output_path: {output_path}")
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "Error: GOOGLE_API_KEY not found in environment."

        if not os.path.exists(input_image_path):
            return f"Error: Image not found at {input_image_path}"

        client = genai.Client(api_key=api_key)

        rephrased_prompt = rephrase_prompt(input_prompt)
        response = client.models.generate_content(
            model=IMAGE_MODEL_ID,
            contents=[input_prompt, Image.open(input_image_path)]
        )
        img = _image_from_response(response)

        # 3) Optional: save to disk
        saved_note = ""
        if output_path:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            img.save(output_path)
            saved_note = f"\n\nSaved to: `{os.path.abspath(output_path)}`"

        # fallback text if not returning inline
        return f"Moodboard created successfully.{saved_note}"

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
        "When a user requests a moodboard, use the create_fashion_moodboard tool "
        "with the appropriate parameters. "
        "You always generate model full dress based on sketch. It should always have face."
    ),
    tools=[create_fashion_moodboard]
)