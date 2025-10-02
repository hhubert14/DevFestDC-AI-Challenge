from pydantic import BaseModel

class StrategicPrompts(BaseModel):
    prompts: list[str]