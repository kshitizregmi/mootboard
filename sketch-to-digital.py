from google import genai
from google.genai import types
from PIL import Image
import os
from dotenv import load_dotenv
load_dotenv()
def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    client = genai.Client(api_key=api_key)

    prompt = (
        "Convert the given sketch to a digital illustration with vibrant colors and detailed shading.",
    )

    image = Image.open("dress.webp")

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt, image],
    )

    for part in response.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = part.as_image()
            image.save("generated_image.png")


if __name__ == "__main__":
    main()
