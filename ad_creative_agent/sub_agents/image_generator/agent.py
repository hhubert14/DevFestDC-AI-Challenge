from google.adk.agents import Agent
from typing import Optional
from vertexai.preview.vision_models import ImageGenerationModel
from vertexai.generative_models import GenerativeModel
import os


# --- IMAGE GENERATION TOOL ---
def generate_ad_image(prompt: str) -> str:
    """
    Generate an ad image using Vertex Imagen and return a clickable file:// link.
    """
    model = ImageGenerationModel.from_pretrained("imagegeneration@005")
    response = model.generate_images(prompt=prompt, number_of_images=1)

    if not response.images or len(response.images) == 0:
        raise ValueError("No images generated.")

    # print("Response:", response.images[0])

    img = response.images[0]
    
    # Create images directory if it doesn't exist
    images_dir = "images"
    os.makedirs(images_dir, exist_ok=True)
    
    # Save to images folder
    filepath = os.path.join(images_dir, "image.png")
    img.save(filepath)

    # abs_path = os.path.abspath(filepath)
    # return f"file://{abs_path}"


# --- PLATFORM TOOLS ---
def generate_facebook_ad(product: str, features: str, image_url: Optional[str] = None) -> dict:
    text_model = GenerativeModel("gemini-2.5-flash")
    prompt = (
        f"Write a Facebook ad for {product} with features: {features}. "
        "Output must follow this format exactly:\n\n"
        "Image Prompt: A detailed visual description for Imagen (include setting, mood, colors, people, background).\n"
    )
    response = text_model.generate_content(prompt, generation_config={"temperature": 0.2})
    ad_text = response.text.strip()

    print("Generated Ad Text:", ad_text)  # Log the generated ad text

    # Extract Image Prompt
    image_prompt = ""
    for line in ad_text.splitlines():
        if line.lower().startswith("image prompt"):
            image_prompt = line.split(":", 1)[-1].strip()

    if not image_prompt:
        raise ValueError("Image prompt is empty. Check the generated ad text.")

    if image_url:
        image_prompt += f" Include elements from: {image_url}"

    image_link = generate_ad_image(image_prompt, "facebook_ad.png")

    return {
        "platform": "Facebook",
        "result": f"Image: {image_link}\n\n"
    }


def generate_tiktok_ad(product: str, features: str, image_url: Optional[str] = None) -> dict:
    text_model = GenerativeModel("gemini-2.5-flash")
    prompt = (
        f"Write a TikTok ad for {product} with features: {features}. "
        "Output must follow this format exactly:\n\n"
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
        "result": f"Image: {image_link}\n\n"
    }


def generate_google_ad(product: str, features: str, image_url: Optional[str] = None) -> dict:
    text_model = GenerativeModel("gemini-2.5-flash")
    prompt = (
        f"Write a Google Ads campaign for {product} with features: {features}. "
        "Output must follow this format exactly:\n\n"
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
        "result": f"Image: {image_link}\n\n"
    }


# --- IMAGE GENERATOR AGENT ---
image_generator_agent = Agent(
    name="image_generator_agent",
    model="gemini-2.5-flash",
    description="Generates ad images for various platforms based on product details.",
    # instruction=(
    #     "Always return exactly:\n"
    #     "- Image Prompt: Detailed visual description.\n"
    #     "- Image: Clickable file:// link to generated PNG.\n"
    # ),
    tools=[generate_ad_image],
)
