from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ModelServer")

ner_pipeline = None
embedding_model = None
MODELS_READY = False

app = FastAPI(title="Axion AI Model Server")

@app.on_event("startup")
async def startup_event():
    global ner_pipeline, embedding_model, MODELS_READY
    logger.info("Model Server starting up...")
    try:
        start_time = time.time()
        logger.info("Loading NER model...")
        ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", grouped_entities=True)
        logger.info(f"NER model loaded in {time.time() - start_time:.2f}s.")
        start_time = time.time()
        logger.info("Loading SentenceTransformer model...")
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info(f"SentenceTransformer loaded in {time.time() - start_time:.2f}s.")
        MODELS_READY = True
        logger.info("Model Server is ready.")
    except Exception as e:
        logger.error(f"FATAL: Could not load AI models. Error: {e}")
        MODELS_READY = False

class VectorizeRequest(BaseModel): text: str
class MaskRequest(BaseModel): text: str

@app.post("/vectorize")
async def vectorize(request: VectorizeRequest):
    if not MODELS_READY: raise HTTPException(status_code=503, detail="Models not ready.")
    embedding = embedding_model.encode(request.text)
    return {"vector": embedding.tolist()}

@app.post("/mask_pii")
async def mask_pii(request: MaskRequest):
    if not MODELS_READY: raise HTTPException(status_code=503, detail="Models not ready.")
    entities = ner_pipeline(request.text)
    masked_text = request.text
    entities.sort(key=lambda e: e['start'])
    for entity in reversed(entities):
        if entity['entity_group'] in ['PER', 'LOC']:
            start, end = entity['start'], entity['end']
            masked_text = masked_text[:start] + '[REDACTED]' + masked_text[end:]
    return {"masked_text": masked_text}

@app.get("/health")
async def health_check():
    if MODELS_READY: return {"status": "ok"}
    else: raise HTTPException(status_code=503, detail="Models not ready")

