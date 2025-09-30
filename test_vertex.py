from google.cloud import aiplatform
from dotenv import load_dotenv
import os

def main():

    load_dotenv()

    project_id = os.getenv("GCP_PROJECT_ID")
    location = "us-central1"  # default region for Vertex AI

    aiplatform.init(project=project_id, location=location)

    print("✅ Vertex AI is initialized for project:", project_id)

if __name__ == "__main__":
    main()
