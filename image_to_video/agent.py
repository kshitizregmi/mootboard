"""
To run this code you need to install the following dependencies:
pip install google-genai pillow
"""
import time
import os
from google import genai
from google.genai import types
import base64
from dotenv import load_dotenv
from PIL import Image
from google.adk.agents import Agent
import io
# Load environment variables
load_dotenv()
MODEL = "veo-3.0-fast-generate-001"

client = genai.Client(
    http_options={"api_version": "v1beta"},
    api_key=os.environ.get("GEMINI_API_KEY"),
)

video_config = types.GenerateVideosConfig(
    aspect_ratio="16:9", # supported values: "16:9" or "16:10"
    number_of_videos=1, # supported values: 1 - 4
    duration_seconds=8, # supported values: 5 - 8
    person_generation="ALLOW_ADULT",
)

def generate(image_path: str = "output/sketch-to-digital/generated_image2.png"):
    image_path = image_path
    img = Image.open(image_path)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    image_bytes = img_byte_arr.getvalue()

    operation = client.models.generate_videos(
        model=MODEL,
        prompt="Make the model in the image walk on a Paris fashion show ramp. Preserve the person's face, dress, and dress color. Show a wide-angle full-body view with audience on the sides. Make sure the model face is same in the video.",
        image=types.Image(image_bytes=image_bytes, mime_type="image/jpeg"),
        config=video_config,
    )

    # Waiting for the video(s) to be generated
    while not operation.done:
        print("Video has not been generated yet. Check again in 10 seconds...")
        time.sleep(10)
        operation = client.operations.get(operation)

    result = operation.result
    if not result:
        print("Error occurred while generating video.")
        return

    generated_videos = result.generated_videos
    if not generated_videos:
        print("No videos were generated.")
        return

    for n, generated_video in enumerate(generated_videos):
        print(f"Video has been generated: {generated_video.video.uri}")
        client.files.download(file=generated_video.video)
        generated_video.video.save(f"output/ramp_walk_video/video2_{n}.mp4") # Saves the video(s)
        print(f"Video {generated_video.video.uri} has been downloaded to video_{n}.mp4.")

root_agent = Agent(
    name="image_to_video_agent",
    model="gemini-2.5-flash",
    description=(
        "Agent that converts images to videos using Gemini models."
    ),
    instruction=(
        "You are a helpful agent who can convert images to videos."
    ),
    tools=[generate],
)