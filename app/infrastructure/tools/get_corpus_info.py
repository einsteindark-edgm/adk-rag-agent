"""
Tool for retrieving detailed information about a specific RAG corpus.
"""

import logging
from google.adk.tools.tool_context import ToolContext
from vertexai import rag

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from .utils import check_corpus_exists, get_corpus_resource_name


def get_corpus_info(
    corpus_name: str,
    tool_context: ToolContext,
) -> dict:
    """
    Get detailed information about a specific RAG corpus, including its files.

    Args:
        corpus_name (str): The full resource name of the corpus to get information about.
                           Preferably use the resource_name from list_corpora results.
        tool_context (ToolContext): The tool context

    Returns:
        dict: Information about the corpus and its files
    """
    logger.info(f"=== Starting get_corpus_info operation ===")
    logger.info(f"Corpus name requested: {corpus_name}")
    
    try:
        # Check if corpus exists
        logger.debug("Checking if corpus exists...")
        corpus_exists = check_corpus_exists(corpus_name, tool_context)
        logger.info(f"Corpus exists: {corpus_exists}")
        
        if not corpus_exists:
            logger.error(f"Corpus '{corpus_name}' does not exist")
            return {
                "status": "error",
                "message": f"Corpus '{corpus_name}' does not exist",
                "corpus_name": corpus_name,
            }

        # Get the corpus resource name
        corpus_resource_name = get_corpus_resource_name(corpus_name)
        logger.info(f"Corpus resource name: {corpus_resource_name}")

        # Try to get corpus details first
        corpus_display_name = corpus_name  # Default if we can't get actual display name
        logger.debug(f"Using corpus display name: {corpus_display_name}")

        # Process file information
        file_details = []
        try:
            # Get the list of files
            logger.info(f"Attempting to list files for corpus: {corpus_resource_name}")
            files = rag.list_files(corpus_resource_name)
            logger.info(f"Successfully retrieved file list. Number of files: {len(list(files)) if files else 0}")
            
            # Re-iterate since we consumed the iterator for counting
            files = rag.list_files(corpus_resource_name)
            
            for idx, rag_file in enumerate(files):
                logger.debug(f"Processing file {idx + 1}...")
                logger.debug(f"File object type: {type(rag_file)}")
                logger.debug(f"File attributes: {dir(rag_file)}")
                # Get document specific details
                try:
                    # Extract the file ID from the name
                    file_id = rag_file.name.split("/")[-1]
                    logger.debug(f"File ID: {file_id}")
                    logger.debug(f"File name: {rag_file.name}")

                    file_info = {
                        "file_id": file_id,
                        "display_name": (
                            rag_file.display_name
                            if hasattr(rag_file, "display_name")
                            else ""
                        ),
                        "source_uri": (
                            rag_file.source_uri
                            if hasattr(rag_file, "source_uri")
                            else ""
                        ),
                        "create_time": (
                            str(rag_file.create_time)
                            if hasattr(rag_file, "create_time")
                            else ""
                        ),
                        "update_time": (
                            str(rag_file.update_time)
                            if hasattr(rag_file, "update_time")
                            else ""
                        ),
                    }
                    
                    # Log file details
                    logger.info(f"File {idx + 1}: {file_info['display_name'] or 'No display name'}")
                    logger.debug(f"  - Source URI: {file_info['source_uri']}")
                    logger.debug(f"  - Create time: {file_info['create_time']}")
                    logger.debug(f"  - Update time: {file_info['update_time']}")
                    
                    # Check for additional attributes
                    if hasattr(rag_file, 'state'):
                        logger.info(f"  - State: {rag_file.state}")
                    if hasattr(rag_file, 'size_bytes'):
                        logger.info(f"  - Size: {rag_file.size_bytes} bytes")
                    if hasattr(rag_file, 'error'):
                        logger.error(f"  - Error: {rag_file.error}")

                    file_details.append(file_info)
                except Exception as e:
                    logger.error(f"Error processing file {idx + 1}: {str(e)}")
                    logger.error(f"Error type: {type(e).__name__}")
                    logger.debug("Continuing to next file...")
                    # Continue to the next file
                    continue
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error("Full error details:", exc_info=True)
            # Continue without file details
            pass

        # Basic corpus info
        logger.info(f"=== get_corpus_info operation completed ===")
        logger.info(f"Total files found: {len(file_details)}")
        
        return {
            "status": "success",
            "message": f"Successfully retrieved information for corpus '{corpus_display_name}'",
            "corpus_name": corpus_name,
            "corpus_display_name": corpus_display_name,
            "file_count": len(file_details),
            "files": file_details,
        }

    except Exception as e:
        logger.error(f"ERROR in get_corpus_info: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error("Full error details:", exc_info=True)
        
        return {
            "status": "error",
            "message": f"Error getting corpus information: {str(e)}",
            "corpus_name": corpus_name,
        }
