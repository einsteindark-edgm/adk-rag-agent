"""
Tool for adding new data sources to a Vertex AI RAG corpus.
"""

import re
import logging
from typing import List

from google.adk.tools.tool_context import ToolContext
from vertexai import rag

# Configure detailed logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from ..config.rag_config import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_EMBEDDING_REQUESTS_PER_MIN,
)
from .utils import check_corpus_exists, get_corpus_resource_name


def add_data(
    corpus_name: str,
    paths: List[str],
    tool_context: ToolContext,
) -> dict:
    """
    Add new data sources to a Vertex AI RAG corpus.

    Args:
        corpus_name (str): The name of the corpus to add data to. If empty, the current corpus will be used.
        paths (List[str]): List of URLs or GCS paths to add to the corpus.
                          Supported formats:
                          - Google Drive: "https://drive.google.com/file/d/{FILE_ID}/view"
                          - Google Docs/Sheets/Slides: "https://docs.google.com/{type}/d/{FILE_ID}/..."
                          - Google Cloud Storage: "gs://{BUCKET}/{PATH}"
                          Example: ["https://drive.google.com/file/d/123", "gs://my_bucket/my_files_dir"]
        tool_context (ToolContext): The tool context

    Returns:
        dict: Information about the added data and status
    """
    logger.info(f"=== Starting add_data operation ===")
    logger.info(f"Corpus name: {corpus_name}")
    logger.info(f"Paths to add: {paths}")
    
    # Check if the corpus exists
    logger.debug("Checking if corpus exists...")
    if not check_corpus_exists(corpus_name, tool_context):
        return {
            "status": "error",
            "message": f"Corpus '{corpus_name}' does not exist. Please create it first using the create_corpus tool.",
            "corpus_name": corpus_name,
            "paths": paths,
        }

    # Validate inputs
    if not paths or not all(isinstance(path, str) for path in paths):
        return {
            "status": "error",
            "message": "Invalid paths: Please provide a list of URLs or GCS paths",
            "corpus_name": corpus_name,
            "paths": paths,
        }

    # Pre-process paths to validate and convert Google Docs URLs to Drive format if needed
    logger.debug("Validating and preprocessing paths...")
    validated_paths = []
    invalid_paths = []
    conversions = []

    for path in paths:
        logger.debug(f"Processing path: {path}")
        if not path or not isinstance(path, str):
            invalid_paths.append(f"{path} (Not a valid string)")
            continue

        # Check for Google Docs/Sheets/Slides URLs and convert them to Drive format
        docs_match = re.match(
            r"https:\/\/docs\.google\.com\/(?:document|spreadsheets|presentation)\/d\/([a-zA-Z0-9_-]+)(?:\/|$)",
            path,
        )
        if docs_match:
            file_id = docs_match.group(1)
            drive_url = f"https://drive.google.com/file/d/{file_id}/view"
            validated_paths.append(drive_url)
            conversions.append(f"{path} → {drive_url}")
            continue

        # Check for valid Drive URL format
        drive_match = re.match(
            r"https:\/\/drive\.google\.com\/(?:file\/d\/|open\?id=)([a-zA-Z0-9_-]+)(?:\/|$)",
            path,
        )
        if drive_match:
            # Normalize to the standard Drive URL format
            file_id = drive_match.group(1)
            drive_url = f"https://drive.google.com/file/d/{file_id}/view"
            validated_paths.append(drive_url)
            if drive_url != path:
                conversions.append(f"{path} → {drive_url}")
            continue

        # Check for GCS paths
        if path.startswith("gs://"):
            validated_paths.append(path)
            continue

        # If we're here, the path wasn't in a recognized format
        invalid_paths.append(f"{path} (Invalid format)")

    # Check if we have any valid paths after validation
    if not validated_paths:
        return {
            "status": "error",
            "message": "No valid paths provided. Please provide Google Drive URLs or GCS paths.",
            "corpus_name": corpus_name,
            "invalid_paths": invalid_paths,
        }

    try:
        # Get the corpus resource name
        corpus_resource_name = get_corpus_resource_name(corpus_name)
        logger.info(f"Corpus resource name: {corpus_resource_name}")

        # Set up chunking configuration
        logger.debug(f"Setting up chunking config: size={DEFAULT_CHUNK_SIZE}, overlap={DEFAULT_CHUNK_OVERLAP}")
        transformation_config = rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(
                chunk_size=DEFAULT_CHUNK_SIZE,
                chunk_overlap=DEFAULT_CHUNK_OVERLAP,
            ),
        )

        # Import files to the corpus
        logger.info(f"Starting import of {len(validated_paths)} files to corpus...")
        logger.info(f"Files to import: {validated_paths}")
        logger.info(f"Max embedding requests per min: {DEFAULT_EMBEDDING_REQUESTS_PER_MIN}")
        
        import_result = rag.import_files(
            corpus_resource_name,
            validated_paths,
            transformation_config=transformation_config,
            max_embedding_requests_per_min=DEFAULT_EMBEDDING_REQUESTS_PER_MIN,
        )
        
        logger.info(f"Import completed! Result: {import_result}")
        logger.info(f"Files imported count: {import_result.imported_rag_files_count}")

        # Set this as the current corpus if not already set
        if not tool_context.state.get("current_corpus"):
            tool_context.state["current_corpus"] = corpus_name

        # Build the success message
        conversion_msg = ""
        if conversions:
            conversion_msg = " (Converted Google Docs URLs to Drive format)"

        return {
            "status": "success",
            "message": f"Successfully added {import_result.imported_rag_files_count} file(s) to corpus '{corpus_name}'{conversion_msg}",
            "corpus_name": corpus_name,
            "files_added": import_result.imported_rag_files_count,
            "paths": validated_paths,
            "invalid_paths": invalid_paths,
            "conversions": conversions,
        }

    except Exception as e:
        logger.error(f"ERROR during import: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Full error details:", exc_info=True)
        
        # Try to get more specific error information
        error_details = {
            "status": "error",
            "message": f"Error adding data to corpus: {str(e)}",
            "error_type": type(e).__name__,
            "corpus_name": corpus_name,
            "paths": paths,
            "validated_paths": validated_paths,
        }
        
        # Add specific error handling for common issues
        if "permission" in str(e).lower():
            error_details["hint"] = "Check that the files are publicly accessible or that the service account has access"
        elif "not found" in str(e).lower():
            error_details["hint"] = "The corpus or file might not exist"
        elif "quota" in str(e).lower():
            error_details["hint"] = "You might have exceeded the API quota. Try reducing max_embedding_requests_per_min"
        
        return error_details
