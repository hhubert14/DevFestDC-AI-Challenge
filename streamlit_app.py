import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# Quick Demo to see the result in my browser
# Using Streamlit to see the result in my browser...
# Load .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Model we used
MODEL = "gemini-2.5-flash"
model = genai.GenerativeModel(MODEL)

# UI
st.title("AI Marketing Ad Generator")

product = st.text_input("Product description")
audience = st.text_input("Target audience")

if st.button("Generate Ads"):
    with st.spinner("Generating ad copy..."):
        prompt = f"""
        Product: {product}
        Audience: {audience}

        Generate 3 ad variations for Facebook, 3 for Google, and 3 for TikTok.
        Each should follow the platform’s typical constraints.
        """
        response = model.generate_content(prompt)
    st.subheader("Ad Variations")
    st.write(response.text)


# Command to run this and test : ## streamlit run streamlit_app.py


# Key takeaways: for myself
# Streamlit is a Python framework that turns Python commands into a live web app (HTML, CSS, JS under the hood). It’s fast to use for hackathons and prototypes - possible to build clean, interactive UIs fast without touching frontend code.