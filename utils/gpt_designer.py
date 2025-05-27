import os 
import base64
import json
from PIL import Image
from io import BytesIO
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

def get_mime_type_from_bytes(img_bytes):
    try:
        img = Image.open(BytesIO(img_bytes))
        format = img.format.lower()
        if format == "jpeg":
            return "image/jpeg"
        elif format == "png":
            return "image/png"
        elif format == "gif":
            return "image/gif"
        elif format == "webp":
            return "image/webp"
    except Exception as e:
        return None

def load_inspiration_images(folder="sample_inputs/inspiration"):
    images = []
    if not os.path.exists(folder):
        print(f"📂 Folder '{folder}' not found. Skipping inspiration loading.")
        return images

    for filename in os.listdir(folder):
        if filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
            path = os.path.join(folder, filename)
            
            # Verify the actual image format
            # Verify image format using Pillow
            try:
                with open(path, "rb") as img_file:
                    raw_bytes = img_file.read()
                    mime_type = get_mime_type_from_bytes(raw_bytes)
                    if not mime_type:
                        print(f"⚠️ Skipping {filename}: Unsupported or invalid format")
                        continue
                    encoded = base64.b64encode(raw_bytes).decode("utf-8")
                    images.append({
                        "name": filename,
                        "base64": encoded
                    })
                    print(f"✅ Loaded inspiration image: {filename}")
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")
                continue
    return images

def load_fabric_inventory(path="fabric_inventory_normalized.json"):
    with open(path, "r") as f:
        return json.load(f)
    
def select_fabric_images(inventory, folder="sample_inputs/clean_jpegs"):
    print("🧵 Available fabrics:")
    for item in inventory:
        print(f"- {item['name']}")
    
    selected_name = input("\n✂️ Enter a keyword or partial name of the fabric you'd like to upcycle: ").strip().lower()
    matches = [item for item in inventory if selected_name in item["name"].lower()]

    if not matches:
        print("❌ Fabric not found.")
        return None, [], []

    # Load all relevant images
    fabric_images = []
    for filename in os.listdir(folder):
        if filename.lower().endswith((".jpg", ".jpeg")) and selected_name in filename:
            path = os.path.join(folder, filename)
            with open(path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                fabric_images.append({"name": filename, "base64": encoded})
                print(f"🧶 Loaded fabric image: {filename}")

    if not fabric_images:
        print("❌ No images found for this fabric.")
        return None, [], []

    return selected_name, fabric_images, matches
    
client = OpenAI()

def suggest_designs(selected_name, inspirations, fabric_images, matching_inventory, num_suggestions=3):

    # Separate image blocks for inspiration and fabric views
    inspiration_blocks = []
    for img in inspirations:
        mime_type = get_mime_type_from_bytes(base64.b64decode(img["base64"]))
        if not mime_type:
            print(f"⚠️ Skipping inspiration image {img['name']}: invalid MIME type")
            continue
        inspiration_blocks.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime_type};base64,{img['base64']}"
            }
        })


    fabric_blocks = []
    for img in fabric_images:
        mime_type = get_mime_type_from_bytes(base64.b64decode(img["base64"]))
        if not mime_type:
            print(f"⚠️ Skipping fabric image {img['name']}: invalid MIME type (detected as {mime_type})")
            continue
        fabric_blocks.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime_type};base64,{img['base64']}"
            }
        })


    fabric_summary = "\n".join(
    f"- {item['name']}: {item['material']}, {item['texture']}, colors: {', '.join(item['colors'])}, embellishments: {item['embellishment_description']}"
    for item in matching_inventory
)

    final_prompt = (
    f"Using the provided inspiration and fabric images for '{selected_name}', generate 3 trendy upcycled clothing ideas.\n\n"
    f"Here are details about the selected fabrics:\n{fabric_summary}\n\n"
    "For each idea:\n"
    "- Name the garment (e.g., halter top, peplum blouse, two-piece set)\n"
    "- Describe exactly what the garment looks like in vivid visual detail\n"
    "- Specify which angle or fabric photo influenced the key design elements\n"
    "- Explain why this matches the user's aesthetic\n"
    "- At the end of each idea, include a DALL·E-style prompt in the format:\n"
    "  DALL·E Prompt: [describe the final garment visually in a single sentence, e.g., 'a white halter crop top with gold embroidery and flared peplum waist, photographed on a hanger']\n\n"
    "Make sure the DALL·E prompt includes fabric type, color, cut, embroidery/embellishment styles, and the setting (e.g., on a model, mannequin, or flat lay)."
)

    # Construct the full chat message with separated sections
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a creative but practical fashion designer."},
            {"role": "user", "content": "These are inspiration photos that reflect my style."},
            {"role": "user", "content": inspiration_blocks},
            {"role": "user", "content": f"These are fabric images for: '{selected_name}'. Use these for upcycling."},
            {"role": "user", "content": fabric_blocks},
            {"role": "user", "content": final_prompt}
        ],
        max_tokens=1000
    )

    return response.choices[0].message.content
    
if __name__ == "__main__":
    inspiration_images = load_inspiration_images("sample_inputs/inspiration")
    fabric_inventory = load_fabric_inventory("fabric_inventory_normalized.json")

    selected_name, fabric_images, matching_inventory = select_fabric_images(fabric_inventory)

    if selected_name and fabric_images:
        suggestions = suggest_designs(selected_name, inspiration_images, fabric_images, matching_inventory)
        print("\n Suggested Clothing Designs:\n")
        print(suggestions)

         # Save for DALL·E generation
        with open("last_suggestions.txt", "w") as f:
            f.write(suggestions)
        print("💾 Saved GPT suggestions to last_suggestions.txt")