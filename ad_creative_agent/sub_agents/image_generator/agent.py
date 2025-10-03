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

    img = response.images[0]
    
    # Create images directory if it doesn't exist
    images_dir = "images"
    os.makedirs(images_dir, exist_ok=True)
    
    # Save to images folder
    filepath = os.path.join(images_dir, "image.png")
    img.save(filepath)

    return "Success! Clickable link to generated image: file://" + os.path.abspath(filepath)

# --- IMAGE GENERATOR AGENT ---
image_generator_agent = Agent(
    name="image_generator_agent",
    model="gemini-2.5-flash",
    description="Generates ad images for various platforms based on product details.",
    tools=[generate_ad_image],
)
