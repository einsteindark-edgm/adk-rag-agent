"""Settings for the A2A server."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Server settings
HOST = os.getenv("A2A_HOST", "0.0.0.0")
PORT = int(os.getenv("A2A_PORT", "8006"))

# Vertex AI settings
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# Agent settings
AGENT_MODEL = os.getenv("AGENT_MODEL", "gemini-2.0-flash-exp")