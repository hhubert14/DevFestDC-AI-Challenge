from ...models.data_models import GraphState
from ...utils.config import get_gemini_api_key
from pydantic import BaseModel



def text_generator_node(state: GraphState):
    key = get_gemini_api_key()
    