from google import genai
from google.genai import types
from google.adk.agents import Agent
from PIL import Image
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def text_to_sketch(
    prompt: str = "A simple black and white pencil sketch of a fashion dress design",
    output_path: str = "output/text-to-sketch/dress_sketch.png",
):
    """
    Generates a clean black-and-white pencil sketch of a dress, with no people, color, or background.

    Args:
        prompt (str, optional): The text prompt describing the dress or outfit.
        output_path (str, optional): Path to save the generated image.

    Returns:
        dict: { "output_path": str, "message": str }
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    client = genai.Client(api_key=api_key)

    # Reinforce strict sketch-only style in the prompt
    refined_prompt = (
        f"{prompt}. Render this as a professional pencil fashion sketch. "
        "Monochrome (black and white only). No color, no background, no person or model, "
        "and no shading beyond light pencil linework."
    )

    # Generate the sketch
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[refined_prompt],
    )

    # Extract image result
    for part in response.parts:
        if part.inline_data is not None:
            result_image = part.as_image()
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            result_image.save(output_path)
            return {
                "output_path": output_path,
                "message": f"Generated sketch saved to {output_path}",
            }

    return {"message": "No image data returned by the model."}


# Define the ADK agent
root_agent = Agent(
    name="text_to_sketch_agent",
    model="gemini-2.5-flash",
    description=(
        "Agent that generates clean, black-and-white pencil sketches of fashion designs. "
        "No color, no people, no background — only the clothing design in line art."
    ),
    instruction=(
        "You generate pure pencil-style sketches of fashion designs. "
        "Never add color, shading, people, or backgrounds."
    ),
    tools=[text_to_sketch],
)