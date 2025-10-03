from google.adk.agents import Agent
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from typing import Optional
import os

def generate_combined_ad(ad_copy: str, image_path: Optional[str] = None, output_path: str = "generated_ad.png") -> str:
    """
    Combines ad copy with an existing image to create a new ad creative.
    
    Args:
        ad_copy: The text content for the ad
        image_path: Path to the image file to use (optional, defaults to images/image.png)
        output_path: Where to save the generated ad
    
    Returns:
        Path to the generated ad image
    """
    client = genai.Client()
    
    # Create prompt that combines the ad copy with image editing instructions
    prompt = f"""
    Create an advertising image that incorporates this ad copy: "{ad_copy}"
    
    Please enhance or modify the provided image to create a compelling advertisement that:
    - Includes the ad copy text in an attractive, readable format
    - Maintains good visual composition and brand appeal
    - Uses appropriate typography and layout for advertising
    - Ensures the text complements rather than overwhelms the image
    """
    
    # Determine image path to use
    if image_path is None:
        image_folder = "images"
        image_path = os.path.join(image_folder, "image.png")
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Base image not found at {image_path}. Please generate an image first.")
    
    # Generate the combined ad creative
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt, Image.open(image_path)],
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))
            ads_dir = "ads"
            os.makedirs(ads_dir, exist_ok=True)
            output_filepath = os.path.join(ads_dir, output_path)
            image.save(output_filepath)
            return output_filepath
    
    # If no inline data found, raise an error
    raise ValueError("No image data found in the response")

# --- AD COMPOSER AGENT ---
ad_composer_agent = Agent(
    name="ad_composer_agent",
    model="gemini-2.5-flash",
    description="Combines ad copy with images to create complete ad creatives for various platforms.",
    tools=[generate_combined_ad],
)
