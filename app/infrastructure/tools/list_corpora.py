"""
Tool for listing all available Vertex AI RAG corpora.
"""

import logging
from typing import Dict, List, Union

from vertexai import rag

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def list_corpora() -> dict:
    """
    List all available Vertex AI RAG corpora.

    Returns:
        dict: A list of available corpora and status, with each corpus containing:
            - resource_name: The full resource name to use with other tools
            - display_name: The human-readable name of the corpus
            - create_time: When the corpus was created
            - update_time: When the corpus was last updated
    """
    logger.info("=== Starting list_corpora operation ===")
    
    try:
        # Get the list of corpora
        logger.debug("Calling rag.list_corpora()...")
        corpora = rag.list_corpora()
        logger.info(f"Successfully retrieved corpora list")

        # Process corpus information into a more usable format
        corpus_info: List[Dict[str, Union[str, int]]] = []
        for idx, corpus in enumerate(corpora):
            logger.debug(f"Processing corpus {idx + 1}...")
            logger.debug(f"Corpus object type: {type(corpus)}")
            logger.debug(f"Corpus name: {corpus.name}")
            logger.debug(f"Corpus display name: {corpus.display_name}")
            corpus_data: Dict[str, Union[str, int]] = {
                "resource_name": corpus.name,  # Full resource name for use with other tools
                "display_name": corpus.display_name,
                "create_time": (
                    str(corpus.create_time) if hasattr(corpus, "create_time") else ""
                ),
                "update_time": (
                    str(corpus.update_time) if hasattr(corpus, "update_time") else ""
                ),
            }
            
            logger.info(f"Corpus {idx + 1}: {corpus_data['display_name']}")
            logger.debug(f"  Resource name: {corpus_data['resource_name']}")
            logger.debug(f"  Created: {corpus_data['create_time']}")
            logger.debug(f"  Updated: {corpus_data['update_time']}")

            corpus_info.append(corpus_data)

        logger.info(f"=== list_corpora operation completed ===")
        logger.info(f"Total corpora found: {len(corpus_info)}")
        
        return {
            "status": "success",
            "message": f"Found {len(corpus_info)} available corpora",
            "corpora": corpus_info,
        }
    except Exception as e:
        logger.error(f"ERROR in list_corpora: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error("Full error details:", exc_info=True)
        
        return {
            "status": "error",
            "message": f"Error listing corpora: {str(e)}",
            "corpora": [],
        }
