import os
import re
import base64
from openai import OpenAI
from dotenv import load_dotenv
import requests

load_dotenv()
client = OpenAI()

# Create output folder
os.makedirs("dalle_outputs", exist_ok=True)

def extract_dalle_prompts(text):
    """
    Extract DALL·E prompts from GPT output that may be written across multiple lines.
    Looks for lines that start with 'DALL·E Prompt:' or similar, then grabs the next line.
    """
    lines = text.splitlines()
    prompts = []
    for i, line in enumerate(lines):
        if "dall" in line.lower() and "prompt" in line.lower():
            # Grab the next non-empty line
            for j in range(i + 1, len(lines)):
                if lines[j].strip():
                    prompts.append(lines[j].strip())
                    break
    return prompts

# Uses OpenAI's image generation to create and save an image based on a prompt.
def generate_and_save_image(prompt, index):
     print(f"🎨 Generating image for: '{prompt}'")

     print(f"🎨 Sending to DALL·E: {prompt}")
    # Call OpenAI's DALL·E API
     response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )

     image_url = response.data[0].url

    # Save URL as .txt and also download image
     image_filename = f"dalle_outputs/design_{index+1}.png"

    # Download the image from the URL
     img_data = requests.get(image_url).content
     with open(image_filename, 'wb') as handler:
        handler.write(img_data)

     print(f"✅ Saved image to: {image_filename}")

def main():
    # Step 1: Load the last GPT output (can modify to read from your pipeline later)
    with open("last_suggestions.txt", "r") as f:
        gpt_response = f.read()

    # Step 2: Extract DALL·E prompts
    prompts = extract_dalle_prompts(gpt_response)
    print(f"\n🧵 Found {len(prompts)} prompts.")

    # Step 3: Generate images
    for i, prompt in enumerate(prompts):
        generate_and_save_image(prompt, i)

if __name__ == "__main__":
    main()
