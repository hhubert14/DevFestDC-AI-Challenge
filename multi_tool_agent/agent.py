from google.adk.agents import Agent
from typing import Optional
from vertexai.preview.vision_models import ImageGenerationModel
from vertexai.generative_models import GenerativeModel
import os


# --- IMAGE GENERATION TOOL ---
def generate_ad_image(prompt: str, filename: str) -> str:
    """
    Generate an ad image using Vertex Imagen and return a clickable file:// link.
    """
    model = ImageGenerationModel.from_pretrained("imagegeneration@005")
    response = model.generate_images(prompt=prompt, number_of_images=1)

    if not response.images or len(response.images) == 0:
        return None

    img = response.images[0]
    img.save(filename)

    abs_path = os.path.abspath(filename)
    return f"file://{abs_path}"


# --- PLATFORM TOOLS ---
def generate_facebook_ad(product: str, features: str, image_url: Optional[str] = None) -> dict:
    text_model = GenerativeModel("gemini-2.5-flash")
    prompt = (
        f"Write a Facebook ad for {product} with features: {features}. "
        "Output must follow this format exactly:\n\n"
        "Ad Copy: 5 sentences, conversational, community-focused, encouraging engagement.\n"
        "Image Prompt: A detailed visual description for Imagen (include setting, mood, colors, people, background).\n"
    )
    response = text_model.generate_content(prompt, generation_config={"temperature": 0.2})
    ad_text = response.text.strip()

    # Extract Image Prompt
    image_prompt = ""
    for line in ad_text.splitlines():
        if line.lower().startswith("image prompt"):
            image_prompt = line.split(":", 1)[-1].strip()

    if image_url:
        image_prompt += f" Include elements from: {image_url}"

    image_link = generate_ad_image(image_prompt, "facebook_ad.png")

    return {
        "platform": "Facebook",
        "result": f"Facebook\n{ad_text}\n\nImage: {image_link}\n\n"
    }


def generate_tiktok_ad(product: str, features: str, image_url: Optional[str] = None) -> dict:
    text_model = GenerativeModel("gemini-2.5-flash")
    prompt = (
        f"Write a TikTok ad for {product} with features: {features}. "
        "Output must follow this format exactly:\n\n"
        "Ad Copy: 5 sentences, playful, catchy, viral style. Encourage trends or FOMO.\n"
        "Image Prompt: A very detailed TikTok-style visual description (vertical, colorful, energetic).\n"
    )
    response = text_model.generate_content(prompt, generation_config={"temperature": 0.2})
    ad_text = response.text.strip()

    # Extract Image Prompt
    image_prompt = ""
    for line in ad_text.splitlines():
        if line.lower().startswith("image prompt"):
            image_prompt = line.split(":", 1)[-1].strip()

    if image_url:
        image_prompt += f" Include visuals from: {image_url}"

    image_link = generate_ad_image(image_prompt, "tiktok_ad.png")

    return {
        "platform": "TikTok",
        "result": f"TikTok\n{ad_text}\n\nImage: {image_link}\n\n"
    }


def generate_google_ad(product: str, features: str, image_url: Optional[str] = None) -> dict:
    text_model = GenerativeModel("gemini-2.5-flash")
    prompt = (
        f"Write a Google Ads campaign for {product} with features: {features}. "
        "Output must follow this format exactly:\n\n"
        "Ad Copy: 5 concise sentences, professional and conversion-focused. Highlight trust and value.\n"
        "Image Prompt: A detailed clean product-focused description (brand-focused, minimal distractions).\n"
    )
    response = text_model.generate_content(prompt, generation_config={"temperature": 0.2})
    ad_text = response.text.strip()

    # Extract Image Prompt
    image_prompt = ""
    for line in ad_text.splitlines():
        if line.lower().startswith("image prompt"):
            image_prompt = line.split(":", 1)[-1].strip()

    if image_url:
        image_prompt += f" Use branding from: {image_url}"

    image_link = generate_ad_image(image_prompt, "google_ad.png")

    return {
        "platform": "Google Ads",
        "result": f"Google Ads\n{ad_text}\n\nImage: {image_link}\n\n"
    }


# --- ROOT AGENT ---
root_agent = Agent(
    name="multi_platform_ad_agent",
    model="gemini-2.5-flash",
    description="Generates structured 5-sentence ad copy + detailed Imagen prompts + clickable links for Facebook, TikTok, and Google Ads.",
    instruction=(
        "Always return exactly:\n"
        "- Ad Copy: 5 sentences, platform-specific style.\n"
        "- Image Prompt: Detailed visual description.\n"
        "- Image: Clickable file:// link to generated PNG.\n"
    ),
    tools=[generate_facebook_ad, generate_tiktok_ad, generate_google_ad],
)
