# streamlit_app.py
import os
import re
import json
import time
from typing import Dict, List, Tuple

import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

from image_generation_VertexAI import generate_ad_image

from pydantic import BaseModel, ValidationError
from typing import List, Dict

class AdsSchema(BaseModel):
    Facebook: List[str]
    Google: List[str]
    TikTok: List[str]




# ---------------------------
# Setup
# ---------------------------
load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    st.stop()  # hard stop: missing key
genai.configure(api_key=GEMINI_KEY)

GEMINI_MODEL = "gemini-2.5-flash"
gemini = genai.GenerativeModel(GEMINI_MODEL)

st.set_page_config(page_title="AI Marketing Ad Generator", layout="wide")
st.title("AI Marketing Ad Generator")

# ---------------------------
# Inputs
# ---------------------------
product = st.text_input("Product description", key="product_input")
audience = st.text_input("Target audience", key="audience_input")
goal = st.selectbox("Ad goal", ["Awareness", "Consideration", "Conversion"], index=0)

st.caption(
    "Click **Generate Ads** to produce 3 texts per platform (Facebook, Google, TikTok). "
    "Images will be auto-generated right after, one per ad."
)

# ---------------------------
# Helpers
# ---------------------------
def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*", "", text, flags=re.MULTILINE)
        text = re.sub(r"```$", "", text, flags=re.MULTILINE)
    return text.strip()


def generate_ads_json(product: str, audience: str) -> Tuple[Dict, str]:
    """
    Ask Gemini to return strict JSON with ad copy.
    """
    prompt = f"""
You are an expert performance marketer and copywriter.

Product: {product}
Target audience: {audience}

Generate **exactly 3** short, punchy ad variations for each of the following platforms:
- Facebook
- Google
- TikTok

Style:
- Clear, persuasive, benefits-first.
- Keep each variation 1–3 sentences, no hashtags for Google; 0–2 tasteful hashtags for Facebook/TikTok.
- No markdown, no emojis for Google. Emojis allowed for Facebook/TikTok.

Return ONLY valid minified JSON in this exact schema:
{{
  "Facebook": ["...", "...", "..."],
  "Google": ["...", "...", "..."],
  "TikTok": ["...", "...", "..."]
}}
"""
    resp = gemini.generate_content(prompt)
    raw = _strip_code_fences(resp.text or "")

    # Implementing the structure validation with pydantic
    try:
        parsed = AdsSchema.parse_raw(raw)
        return parsed.dict(), None
    except ValidationError as e:
        return None, f"❌ Schema validation error: {e}\nRaw output:\n{raw}"
    except json.JSONDecodeError as e:
        return None, f"❌ JSON parsing error: {e}\nRaw output:\n{raw}"



def visual_prompt_from_ad(ad_text: str, product: str, audience: str, goal: str, platform: str) -> str:
    """
    Create a highly detailed, platform-aware visual prompt from the ad copy.
    We keep it text-only; image model will read and follow these instructions.
    """
    platform_guidelines = {
        "Facebook": """
- Composition: product hero centered, lifestyle context, friendly human presence when appropriate.
- Framing: square-like framing; think "works well as 1:1". Clear focal point.
- Text in image: avoid embedded text; rely on visuals.
- Vibe: warm, inviting, authentic; real-world usage; subtle brand feel.
""",
        "Google": """
- Composition: clean, minimalist product-centric laydown on a tidy background.
- Framing: think "works well as 1200x628 landscape banner"; ample negative space.
- Text in image: none.
- Vibe: crisp, polished, high-clarity e-commerce product visual.
""",
        "TikTok": """
- Composition: vertical storytelling moment; dynamic, human-in-action scene.
- Framing: think "works well as 9:16"; subject large, energetic motion or expressive emotion.
- Text in image: avoid; keep visual clean.
- Vibe: fun, high-energy, modern social-video aesthetic with cinematic lighting.
""",
    }

    brief = f"""
Turn the following ad copy into a single, precise **visual description** for an image generator.
The goal is to convey what the image should *look like* (objects, scene, colors, mood, lighting, camera framing).
No camera brands, no celebrity likeness, no trademarks, no text overlays.

Product: {product}
Audience: {audience}
Marketing goal: {goal}
Platform: {platform}
Platform-specific visual guidelines:
{platform_guidelines.get(platform, "")}

Ad copy:
\"\"\"{ad_text}\"\"\"

Write the final prompt as one paragraph, 80–160 words, covering:
- Subject(s) and actions
- Clear product placement and details
- Setting and props
- Lighting, color palette, mood
- Composition that fits the platform guidance above
Return ONLY the paragraph (no preface, no bullets, no markdown).
"""
    out = gemini.generate_content(brief).text or ""
    return _strip_code_fences(out)


# ---------------------------
# Session state
# ---------------------------
if "ads" not in st.session_state:
    st.session_state["ads"] = None
if "visuals" not in st.session_state:
    st.session_state["visuals"] = None
if "images" not in st.session_state:
    st.session_state["images"] = None  # dict: platform -> list of paths or None


# ---------------------------
# Generate
# ---------------------------
col_left, col_right = st.columns([2, 1])

with col_left:
    if st.button("Generate Ads"):
        if not product.strip() or not audience.strip():
            st.warning("Please fill Product and Audience.")
            st.stop()

        with st.spinner("Generating ad copy with Gemini..."):
            ads, err = generate_ads_json(product, audience)

        if err:
            st.error(err)
            st.stop()

        st.session_state["ads"] = ads
        st.session_state["visuals"] = {}
        st.session_state["images"] = {"Facebook": [None, None, None],
                                      "Google": [None, None, None],
                                      "TikTok": [None, None, None]}

        # Create detailed visual prompts per ad & auto-generate images
        platforms = ["Facebook", "Google", "TikTok"]
        total = sum(len(ads.get(p, [])) for p in platforms)
        progress = st.progress(0, text="Creating visual prompts & generating images...")

        done = 0
        for platform in platforms:
            variations: List[str] = ads.get(platform, []) or []
            st.session_state["visuals"][platform] = []
            for i, ad_text in enumerate(variations):
                # 1) Visual prompt
                vprompt = visual_prompt_from_ad(ad_text, product, audience, goal, platform)
                st.session_state["visuals"][platform].append(vprompt)

                # 2) Generate image (prompt-only; supported by your SDK)
                img_path, img_err = generate_ad_image(
                    vprompt, out_dir="generated", basename=f"{platform.lower()}-{i+1}"
                )
                if img_err:
                    st.session_state["images"][platform][i] = None
                    st.warning(f"{platform} #{i+1} image failed: {img_err}")
                else:
                    st.session_state["images"][platform][i] = img_path

                done += 1
                progress.progress(done / max(total, 1))

        progress.empty()
        st.success("Ads + images generated.")

# ---------------------------
# Display
# ---------------------------
ads = st.session_state.get("ads")
images = st.session_state.get("images")
visuals = st.session_state.get("visuals")

if ads:
    st.subheader("Ads Preview")
    for platform in ["Facebook", "Google", "TikTok"]:
        st.markdown(f"### {platform}")
        cols = st.columns(3)
        for i, ad_text in enumerate(ads.get(platform, []) or []):
            with cols[i % 3]:
                st.write(f"**{platform} #{i+1}:** {ad_text}")
                vprompt = (visuals or {}).get(platform, [])
                if i < len(vprompt):
                    with st.expander("Visual prompt used"):
                        st.write(vprompt[i])

                path = (images or {}).get(platform, [None, None, None])[i] if images else None
                if path:
                    st.image(path, use_container_width =True)
                    with open(path, "rb") as f:
                        st.download_button(
                            label="⬇️ Download image",
                            data=f,
                            file_name=os.path.basename(path),
                            mime="image/png",
                            key=f"dl-{platform}-{i}",
                        )

    # Also offer ads JSON download
    st.download_button(
        "Download Ads JSON",
        data=json.dumps(ads, indent=2),
        file_name="ads.json",
        mime="application/json",
    )
