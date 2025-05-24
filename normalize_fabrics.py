import json
import os

INPUT_FILE = "fabric_inventory.json"
OUTPUT_FILE = "fabric_inventory_normalized.json"

def normalize_embellishments(entry):
    emb = entry.get("embellishments")

    if emb is True or emb == "yes":
        entry["embellishments"] = ["unspecified embellishment"]
    elif emb is False or emb == "none" or emb is None:
        entry["embellishments"] = []
    elif isinstance(emb, str):
        entry["embellishments"] = [emb.strip()]
    elif isinstance(emb, list):
        entry["embellishments"] = [e.strip() for e in emb if isinstance(e, str)]
    else:
        entry["embellishments"] = []

def fix_typos(entry):
    if "detial" in entry["name"]:
        entry["name"] = entry["name"].replace("detial", "detail")
    if "detial" in entry["image_main"]:
        entry["image_main"] = entry["image_main"].replace("detial", "detail")

def normalize_inventory():
    with open(INPUT_FILE, "r") as f:
        inventory = json.load(f)

    for entry in inventory:
        normalize_embellishments(entry)
        fix_typos(entry)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(inventory, f, indent=2)

    print(f"✅ Normalized {len(inventory)} items and saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    normalize_inventory()
