import os
from dotenv import load_dotenv

load_dotenv()

def initialize_environment():
    required_vars = {
        "GEMINI_API_KEY": "Google AI Studio API key"
    }
    missing_vars = []
    for var_name, var_desc in required_vars.items():
        if not os.getenv(var_name):
            missing_vars.append(f"{var_name} ({var_desc})")

    if missing_vars:
        raise EnvironmentError(
            f"""Missing environment variables:
{"\n".join(f"- {var}" for var in missing_vars)}
Please create a .env file with these variables."""
        )

initialize_environment()

def get_gemini_api_key():
    return os.getenv("GEMINI_API_KEY")