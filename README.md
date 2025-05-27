# Fashion Upcycle AI

This is a Streamlit-powered AI assistant that helps users **upcycle traditional Indian fabrics** into modern, trendy clothing designs using **GPT-4o** and **DALL·E 3**.

---

## Tech Stack

- Python
- Streamlit
- OpenAI API GPT4o
- OpenAI API DallE
- Pillow (PIL)


## Features

- Upload photos of old fabrics (saris, kurtis, dupattas, etc.) to have them analyzed
- Generate unique clothing design ideas which are inspired by your liked patterns/cutouts using GPT-4o
- Get mockup images using DALL·E 3
- Personalized to your aesthetic using inspiration uploads
- Use cases: sustainable fashion, creative reuse, design exploration

---

## How It Works

1. **Upload fabric photos** → automatically processed and categorized
2. **Select a fabric group** → system loads and analyzes all variants (detail, back, full), storing the required fields in a JSON
3. **(Optional)** Upload inspiration images (or use preloaded ones)
4. **Generate ideas** → GPT-4o creates 3 upcycle suggestions
5. **Mockups generated** → DALL·E turns prompts into visual outputs

---

## Setup Instructions

1. create a .env file with your OpenAI Secret Key
2. 
```bash
# Clone the repo
git clone https://github.com/your-username/fashion_ai_project.git
cd fashion_ai_project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run app.py

```
## Future Improvements
- Multi-user session tracking
- Save multiple designs with tags
- Custom design editing UI


