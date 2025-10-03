import os

import google.auth
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

from .sub_agents.copy_generator.agent import copy_generator_agent
from .sub_agents.image_generator.agent import image_generator_agent
from .sub_agents.ad_composer.agent import ad_composer_agent

PROMPT = """
You are an advertising copy generator. Your task is to create engaging and persuasive ad copy for various products. Please provide a brief description of the product, its target audience, and any specific features or benefits you want to highlight. Based on this information, generate a compelling ad copy that captures attention and drives interest.
"""

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    instruction=PROMPT,
    tools=[
        AgentTool(agent=copy_generator_agent),
        AgentTool(agent=image_generator_agent),
        AgentTool(agent=ad_composer_agent),
    ],
)