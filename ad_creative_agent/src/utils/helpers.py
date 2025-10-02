from google import genai
from pydantic import ValidationError

from ..utils.config import get_gemini_api_key
from ..models.prompt_models import StrategicPrompts
from ..models.data_models import CreativeBrief

client = genai.Client(api_key=get_gemini_api_key())

def create_strategic_text_prompts(brief: CreativeBrief):
    prompt = f"""You are an expert marketing strategist. Based on the following campaign brief, generate 5 strategic prompts that will be used to create compelling ad copy.

    Campaign Brief:
    - Product: {brief.product_description}
    - Target Audience: {brief.target_audience}
    - Platform: {brief.platform}

    Each prompt should:
    1. Be specific and actionable for copywriters
    2. Focus on different angles (emotional, rational, urgency, benefits, etc.)
    3. Be designed to generate high-converting ad copy for {brief.platform}
    4. Consider the target audience and platform requirements
    5. Be between 20-50 words each

    Return exactly 5 strategic prompts that will help create diverse, effective ad variations optimized for {brief.platform}."""

    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": StrategicPrompts,
                },
            )
            strategic_prompts = StrategicPrompts.model_validate_json(response.text)
            return strategic_prompts.prompts
        except ValidationError as e:
            print(f"Validation error on attempt {attempt + 1}: {e}")
            if attempt == 4:  # Last attempt
                print("All retry attempts failed, returning fallback prompts")
                return [
                    "Create compelling ad copy that highlights the main benefits of the product",
                    "Write emotional copy that connects with the target audience's pain points", 
                    "Develop urgent copy that encourages immediate action",
                    "Focus on social proof and testimonials in your ad copy",
                    "Emphasize unique selling propositions that differentiate from competitors"
                ]
            continue
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise