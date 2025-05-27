# test_flow.py
import base64
from utils import gpt_designer

# Load 1 valid fabric image
with open("clean_jpegs/white_circle_kurti_full.jpg", "rb") as f:
    encoded = base64.b64encode(f.read()).decode("utf-8")

fabric_images = [{
    "name": "white_circle_kurti_full.jpg",
    "base64": encoded
}]

# Dummy inventory description for GPT prompt
matching_inventory = [{
    "name": "white_circle_kurti",
    "material": "cotton",
    "texture": "soft woven",
    "colors": ["white", "yellow", "brown"],
    "embellishment_description": "circular printed motifs"
}]

# Load inspiration images
inspiration_images = gpt_designer.load_inspiration_images("inspiration")

# Call GPT to get fashion ideas
suggestions = gpt_designer.suggest_designs(
    selected_name="white_circle_kurti",
    inspirations=inspiration_images,
    fabric_images=fabric_images,
    matching_inventory=matching_inventory
)

# Print and save
print("\n🧵 Suggested Clothing Designs:\n")
print(suggestions)

with open("last_suggestions.txt", "w") as f:
    f.write(suggestions)
print("💾 Saved to last_suggestions.txt")
