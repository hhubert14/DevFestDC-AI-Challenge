import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env
load_dotenv()

# Configure Gemini with API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use a lightweight model for speed
model = genai.GenerativeModel("gemini-2.5-flash")

# Test prompt
prompt = "Write 3 ad headlines for a new eco-friendly water bottle."
response = model.generate_content(prompt)

print("\n=== Gemini Response ===\n")
print(response.text)
