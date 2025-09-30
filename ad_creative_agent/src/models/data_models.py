from pydantic import BaseModel

class CreativeBrief(BaseModel):
    product_description: str
    target_audience: str
    platform: str # "Facebook", "TikTok", etc.

class AdCopy(BaseModel):
    headline: str
    body: str
    generation_prompt: str

class RawImage(BaseModel):
    image_path: str
    generation_prompt: str

class AdCreative(BaseModel):
    ad_copy: AdCopy
    raw_image: RawImage
    composed_image_path: str
    quality_score: int | None = None
    performance_metrics: dict | None = None

# The state that will be passed between nodes in our graph
class GraphState(BaseModel):
    brief: CreativeBrief
    generated_text: list[AdCopy]
    generated_images: list[RawImage]
    composed_ads: list[AdCreative]
    final_recommendation: str | None = None
