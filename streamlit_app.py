import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# Quick Demo to see the result in my browser
# Using Streamlit to see the result in my browser...
# Load .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Model we use
MODEL = "gemini-2.5-flash"
model = genai.GenerativeModel(MODEL)

# UI
st.title("AI Marketing Ad Generator")

product = st.text_input("Product description")
audience = st.text_input("Target audience")

if st.button("Generate Ads"):
    if not product.strip() or not audience.strip():
        st.warning("⚠️ Please fill in both Product and Audience before generating ads.")
    else:
        with st.spinner("Generating ad copy..."):
            prompt = f"""
            Product: {product}
            Audience: {audience}

            Generate 3 ad variations for each platform: Facebook, Google, TikTok.

            Return ONLY valid JSON. 
            Do not include explanations, markdown, or code fences.
            Output must exactly match this structure:
            {{
              "Facebook": ["ad1", "ad2", "ad3"],
              "Google": ["ad1", "ad2", "ad3"],
              "TikTok": ["ad1", "ad2", "ad3"]
            }}
            """
            response = model.generate_content(prompt)  

        import json
        import re

        raw_text = response.text.strip()

        try:
            if raw_text.startswith("```"):
                raw_text = re.sub(r"^```(?:json)?", "", raw_text, flags=re.MULTILINE)
                raw_text = re.sub(r"```$", "", raw_text, flags=re.MULTILINE)
                raw_text = raw_text.strip()

            ads = json.loads(raw_text)

            if ads.get("Facebook"):
                st.markdown("## Facebook Ads")
                st.write("\n\n".join([ad for ad in ads["Facebook"] if ad.strip()]))

            if ads.get("Google"):
                st.markdown("## Google Ads")
                st.write("\n\n".join([ad for ad in ads["Google"] if ad.strip()]))

            if ads.get("TikTok"):
                st.markdown("## TikTok Ads")
                st.write("\n\n".join([ad for ad in ads["TikTok"] if ad.strip()]))

            if any(ads.get(p) for p in ["Facebook", "Google", "TikTok"]):
                st.download_button(
                    label="📥 Download Ads JSON",
                    data=json.dumps(ads, indent=2),
                    file_name="ads.json",
                    mime="application/json"
                )

        except Exception:
            st.error("⚠️ Could not parse Gemini's response. Please try again.")
            st.text(raw_text)  # 👈 fallback always safe now

# Command to run this and test : ## streamlit run streamlit_app.py
# Might need to have Streamlit installed too : pip install streamlit


# Key takeaways: for myself
# Streamlit is a Python framework that turns Python commands into a live web app (HTML, CSS, JS under the hood). It’s fast to use for hackathons and prototypes - possible to build clean, interactive UIs fast without touching frontend code.

# We can change later how we want gemini to return the data depending on what we need .