import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

prompt = "Write 3 ad headlines for a new eco-friendly water bottle."
response = model.generate_content(prompt)

print("\n=== Gemini Response ===\n")
print(response.text)
