"""Vertex AI RAG Agent Package.

This package implements a Clean Architecture RAG agent using A2A protocol.
"""

import vertexai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Vertex AI
# This happens when the package is imported
project = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

if project:
    vertexai.init(project=project, location=location)
    print(f"Initialized Vertex AI with project: {project}, location: {location}")
else:
    print("Warning: GOOGLE_CLOUD_PROJECT not set. Vertex AI not initialized.")