import os
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ModelDownloader")

def main():
    logger.info("--- Starting AI Model Download ---")
    try:
        logger.info("Downloading NER model (dslim/bert-base-NER)...")
        pipeline('ner', model='dslim/bert-base-NER')
        logger.info("NER model downloaded successfully.")

        logger.info("Downloading SentenceTransformer model (all-MiniLM-L6-v2)...")
        SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("SentenceTransformer model downloaded successfully.")
        
        logger.info("--- All models have been downloaded and cached successfully. ---")
    except Exception as e:
        logger.error(f"A critical error occurred during model download: {e}")
        exit(1)

if __name__ == "__main__":
    main()

