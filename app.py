# app.py

import streamlit as st
import os
import json
from utils import fabric_loader, gpt_designer, dalle_generator

st.set_page_config(page_title="Fashion Upcycle AI", layout="wide")
st.title("👗 Fashion Upcycle AI")

# ──────────────────────────────────────────────────────────────
# 🔁 1. Optional: Upload New Fabric Images
# ──────────────────────────────────────────────────────────────
st.header("1️⃣ Upload New Fabric Images (Optional)")

uploaded_files = st.file_uploader(
    "Upload new fabric images (.jpg, .jpeg, .png)", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        image_path = os.path.join("images", file.name)
        with open(image_path, "wb") as f:
            f.write(file.getbuffer())
        st.image(image_path, caption=file.name, use_column_width=True)

    if st.button("🔍 Analyze New Fabrics"):
        results = fabric_loader.process_images_once(folder="images")
        st.success(f"✅ Processed and saved {len(results)} new fabrics.")

# ──────────────────────────────────────────────────────────────
# 🧵 2. Select a Fabric (Grouped Views)
# ──────────────────────────────────────────────────────────────
st.header("2️⃣ Choose a Fabric to Upcycle")

# Load existing fabric inventory
inventory = gpt_designer.load_fabric_inventory()

# Group fabrics by base name
def get_base_name(name):
    suffixes = ["_detail", "_back", "_dupatta", "_bottoms", "_front", "_full"]
    for suffix in suffixes:
        if name.endswith(suffix):
            return name[:-len(suffix)]
    return name

grouped_fabrics = {}
for entry in inventory:
    base = get_base_name(entry['name'])
    if base not in grouped_fabrics:
        grouped_fabrics[base] = []
    grouped_fabrics[base].append(entry)

base_fabric_names = list(grouped_fabrics.keys())
selected_base = st.selectbox("Select a fabric group", base_fabric_names)

selected_inventory = grouped_fabrics[selected_base]

# Load all matching images
fabric_images = []
for filename in os.listdir("clean_jpegs"):
    if selected_base in filename:
        path = os.path.join("clean_jpegs", filename)
        with open(path, "rb") as f:
            encoded = f.read()
            fabric_images.append({"name": filename, "base64": encoded})
        st.image(path, caption=filename, width=150)

# ──────────────────────────────────────────────────────────────
# 💡 3. Use Existing Inspirations + Optional Uploads
# ──────────────────────────────────────────────────────────────
st.header("3️⃣ Style Inspirations (Optional)")

st.markdown("We’ve preloaded some inspiration images. You can upload more if you want to add to them.")

# Load existing inspiration from disk
inspiration_images = gpt_designer.load_inspiration_images("inspiration")

# Show existing ones first
if inspiration_images:
    st.subheader("🖼️ Existing Inspirations")
    for img in inspiration_images:
        st.image(f"inspiration/{img['name']}", caption=img['name'], width=150)

# Let user upload more (optional)
uploaded_inspo = st.file_uploader(
    "Upload additional inspiration images (optional)", 
    type=["jpg", "jpeg"], 
    accept_multiple_files=True, 
    key="extra_inspo"
)

if uploaded_inspo:
    st.subheader("➕ New Inspirations You Uploaded")
    for file in uploaded_inspo:
        path = os.path.join("inspiration", file.name)
        with open(path, "wb") as f:
            f.write(file.getbuffer())
        with open(path, "rb") as img:
            encoded = img.read()
            inspiration_images.append({"name": file.name, "base64": encoded})
        st.image(path, caption=file.name, width=150)

# ──────────────────────────────────────────────────────────────
# 🧠 4. Generate Designs with GPT + DALL·E
# ──────────────────────────────────────────────────────────────
st.header("4️⃣ Generate AI Suggestions + Mockups")

if st.button("🎨 Generate Clothing Design Ideas"):
    with st.spinner("Generating ideas with GPT-4o..."):
        print("🧪 Sending fabric images:")
        for img in fabric_images:
            print(f"  - {img['name']}")

        suggestions = gpt_designer.suggest_designs(
            selected_name=selected_base,
            inspirations=inspiration_images,
            fabric_images=fabric_images,
            matching_inventory=selected_inventory
        )

        st.markdown("## ✏️ Suggested Clothing Ideas")
        st.markdown(suggestions)

        with open("last_suggestions.txt", "w") as f:
            f.write(suggestions)

    with st.spinner("Generating images with DALL·E..."):
        prompts = dalle_generator.extract_dalle_prompts(suggestions)
        print("🧵 PROMPTS BEING SENT TO DALL·E:")
        for i, p in enumerate(prompts):
            print(f"{i+1}. {p}")

        for i, prompt in enumerate(prompts):
            dalle_generator.generate_and_save_image(prompt, i)
            st.image(f"dalle_outputs/design_{i+1}.png", caption=prompt, use_column_width=True)

    st.success("✅ Done! Designs and mockups are shown above.")

