from PIL import Image
img = Image.open("clean_jpegs/white_circle_kurti_full.jpg")
img.verify()
print("✅ Image is valid.")
