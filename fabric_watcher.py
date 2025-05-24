# fabric_watcher.py

# Used for openai secret key
from dotenv import load_dotenv
load_dotenv()

# This is so the script can interact with OS
# Needed tp cjecl of folders/files exist, to move files, to get file names, to create folders
import os 

import json

# Gives access to time related functions such as sleeping
import time

import base64

import ast

# Loads openai Python client library
from openai import OpenAI

# Helps for moving files
import shutil

WATCH_FOLDER = "images/"
OUTPUT_JSON = "fabric_inventory.json"
PROCESSED_FOLDER = "processed_images/"

client = OpenAI()

os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(WATCH_FOLDER, exist_ok=True)

def generate_fabric_metadata(image_path):
    # Read the image file
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    # Get the filename
    filename = os.path.basename(image_path)

    # Infer type of image from the filename (based on your convention)
    if "detail" in filename:
        image_type_description = "This image is a close-up detail shot of the fabric's embellishments or texture."
    elif "back" in filename:
        image_type_description = "This image shows the back of the fabric or garment."
    elif "dupatta" in filename:
        image_type_description = "This image is of the dupatta (scarf) associated with the outfit."
    elif "bottoms" in filename:
        image_type_description = "This image is of the pants or bottom piece of the outfit."
    else:
        image_type_description = "This is the main photo of the full garment or fabric."

    # Construct prompt
    prompt = (
        f"{image_type_description}\n\n" #the f is formatted string literall allowing you to enter variables into string
        "Please describe:\n"
        "1. The material (e.g., silk, cotton, net)\n"
        "2. The texture (e.g., smooth, sheer, stiff)\n"
        "3. Primary colors present\n"
        "4. Any visible embellishments (e.g., embroidery, mirror work, sequins)\n"
        "5. Whether it has borders or ornate zones, and where\n"
        "Respond in JSON format with these keys: material, texture, colors, embellishments, embellishment_description."
    )

    # Encode the image into base64
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    # Send request using base64 data to GPT-4o
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful fashion assistant."},
            {"role": "user", "content": prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=500
    )

    # Parse and return
    message_content = response.choices[0].message.content
    print(f"\n Raw GPT response for {filename}:\n{repr(message_content)}\n")

    # Clean the response more systematically
    cleaned_content = clean_json_response(message_content)
    print(f"🔍 Cleaned GPT content:\n{cleaned_content}\n")

    # Try to parse it
    try:
        fabric_data = json.loads(cleaned_content)
        print(f"✅ Successfully parsed JSON for {filename}")
        return fabric_data
    except json.JSONDecodeError as err:
        print(f"❌ Failed to parse JSON for {filename}: {err}")
        print(f"🔬 Error position: line {err.lineno}, column {err.colno}")
        print(f"🔬 Problematic character: '{cleaned_content[err.pos] if err.pos < len(cleaned_content) else 'EOF'}'")
         # Try additional fallback methods
        fallback_result = try_fallback_parsing(cleaned_content, filename)
        if fallback_result:
            return fallback_result
        
        return None

    #fabric_data = json.loads(message_content) # Turns JSON string --> Python dict
    #return fabric_data # Returns it to the script

def clean_json_response(message_content):
    """Clean the GPT response to extract valid JSON"""
    if not message_content:
        return ""
    
    # Remove outer single quotes if present
    content = message_content.strip()
    if content.startswith("'") and content.endswith("'"):
        content = content[1:-1]
    
    # Split into lines for processing
    lines = content.strip().splitlines()
    
    # Remove markdown code blocks
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    
    # Rejoin and clean
    cleaned = "\n".join(lines).strip()
    
    # Remove any remaining outer quotes
    if cleaned.startswith('"') and cleaned.endswith('"'):
        cleaned = cleaned[1:-1]
    
    return cleaned

def try_fallback_parsing(content, filename):
    """Try various fallback methods to parse the JSON"""
    print(f"🩹 Trying fallback parsing methods for {filename}...")
    
    # Method 1: Try ast.literal_eval
    try:
        print("   Trying ast.literal_eval...")
        result = ast.literal_eval(content)
        if isinstance(result, dict):
            print("   ✅ ast.literal_eval succeeded!")
            return result
    except Exception as e:
        print(f"   ❌ ast.literal_eval failed: {e}")
    
    # Method 2: Try to find JSON within the content
    try:
        print("   Trying to extract JSON substring...")
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_substring = content[start_idx:end_idx+1]
            result = json.loads(json_substring)
            print("   ✅ JSON substring extraction succeeded!")
            return result
    except Exception as e:
        print(f"   ❌ JSON substring extraction failed: {e}")
    
    # Method 3: Try manual creation of a basic structure
    try:
        print("   Creating fallback structure...")
        fallback_data = {
            "material": "unknown",
            "texture": "unknown", 
            "colors": ["unknown"],
            "embellishments": False,
            "embellishment_description": "Could not parse response"
        }
        print("   ✅ Using fallback structure")
        return fallback_data
    except Exception as e:
        print(f"   ❌ Even fallback failed: {e}")
    
    return None

def save_fabric_entry(fabric_data, image_path, output_file="fabric_inventory.json"):
    if not fabric_data:
        print(f"⚠️ No fabric data to save for {image_path}")
        return
        
    # Load existing inventory
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        with open(output_file, "r") as f:
            inventory = json.load(f)
    else:
        inventory = []
    
    # Generate a new unique ID
    fabric_id = f"fabric_{len(inventory) + 1:03d}"

    # Determine the fabric name from image file
    filename = os.path.basename(image_path)
    fabric_name = filename.lower().replace(".jpg", "").replace(".jpeg", "").replace(".png", "")

    # Build full record
    fabric_entry = {
        "id": fabric_id,
        "name": fabric_name,
        "image_main": image_path, 
        **fabric_data,
        "is_wearable_as_is": "",
        "size_issue": "",
        "upcycle_only": True,
        "notes": ""
    }

    # Append to JSON
    inventory.append(fabric_entry)
    with open(output_file, "w") as f:
        json.dump(inventory, f, indent=2)

    # Move the image to processed_images/
    os.makedirs("processed_images", exist_ok=True)
    new_path = os.path.join("processed_images", filename)
    shutil.move(image_path, new_path)

    print(f"✅ Saved {fabric_id} and moved image to processed_images/")

def main():
    while True:
        image_folder = "images"
        if not os.path.exists(image_folder):
            print(f"⚠️ Images folder '{image_folder}' doesn't exist. Creating it...")
            os.makedirs(image_folder)
            
        image_files = [f for f in os.listdir(image_folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        
        if not image_files:
            print("📭 No images found. Waiting...")
            time.sleep(5)
            continue

        for filename in image_files:
            image_path = os.path.join(image_folder, filename)
            print(f"🔄 Processing {filename}...")

            try:
                fabric_data = generate_fabric_metadata(image_path)
                if fabric_data:
                    save_fabric_entry(fabric_data, image_path)
                else:
                    print(f"⚠️ Could not process {filename} - skipping")
            except Exception as e:
                print(f"💥 Error processing {filename}: {e}")
                import traceback
                traceback.print_exc()
                
        print(f"⏰ Processed {len(image_files)} images. Waiting 5 seconds...")
        time.sleep(5)
    
if __name__ == "__main__":
    main()