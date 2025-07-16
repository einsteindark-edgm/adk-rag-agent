"""Entry point for A2A Document Extraction Server."""
from app.main.a2a_main import run_server

if __name__ == "__main__":
    # CRITICAL: This starts the A2A server, not a regular HTTP server
    run_server()