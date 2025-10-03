from google.adk.agents import Agent

PROMPT = f"""
Create an engaging ad copy for the following product based on its description and target audience. Keep it concise and persuasive.
"""

copy_generator_agent = Agent(
    name="copy_generator_agent",
    model="gemini-2.5-flash",
    instruction=PROMPT,
    output_key="copy_generator_agent_output",
)