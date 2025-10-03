# image_generation_VertexAI.py
import os
import uuid
from typing import Tuple, Optional

import vertexai
from vertexai.vision_models import ImageGenerationModel
from dotenv import load_dotenv
load_dotenv()


_PROJECT = os.getenv("GCP_PROJECT_ID")
_LOCATION = os.getenv("GCP_LOCATION", "us-central1")

_model_singleton: Optional[ImageGenerationModel] = None
_vertex_inited = False


def _ensure_vertex():
    """Init Vertex AI exactly once."""
    global _vertex_inited
    if not _vertex_inited:
        if not _PROJECT:
            raise RuntimeError(
                "GCP_PROJECT_ID is missing in environment. "
                "Set it in your .env (and load it before importing this module)."
            )
        vertexai.init(project=_PROJECT, location=_LOCATION)
        _vertex_inited = True


def _get_model() -> ImageGenerationModel:
    """Lazily load the public image model that is available for most projects."""
    global _model_singleton
    _ensure_vertex()
    if _model_singleton is None:
        # Stay on the widely available model — do NOT change this name.
        _model_singleton = ImageGenerationModel.from_pretrained("imagegeneration@005")
    return _model_singleton


def _safe_slug(text: str, max_len: int = 40) -> str:
    keep = []
    for ch in text.lower():
        if ch.isalnum():
            keep.append(ch)
        elif ch in (" ", "-", "_"):
            keep.append("-")
    slug = "".join(keep).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug[:max_len] or "image"


def generate_ad_image(
    prompt: str,
    out_dir: str = "generated",
    basename: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Generate a single image from a text prompt and save it to disk.

    Returns:
        (path, error) where path is the PNG file path if successful, else None.
    """
    try:
        os.makedirs(out_dir, exist_ok=True)
        model = _get_model()

        # IMPORTANT: keep only supported args; older SDKs reject extra kwargs.
        images = model.generate_images(prompt=prompt)

        if not images:
            return None, "Model returned no images."
        filename = f"{_safe_slug(basename or prompt)}-{uuid.uuid4().hex[:8]}.png"
        file_path = os.path.join(out_dir, filename)
        images[0].save(file_path)
        return file_path, None
    except Exception as e:  # broad by design to surface any SDK/network/safety errors
        return None, f"Vertex generation error: {e}"
