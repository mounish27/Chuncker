from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import tempfile
import os
from pipeline.document_pipeline import DocumentPipeline
from config import AppConfig
from utils.file_loader import SUPPORTED_EXTENSIONS

pipeline = DocumentPipeline()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-warm OCR model at startup so the first request isn't slow
    pipeline.ocr_engine._get_reader()
    yield

app = FastAPI(
    title="Arcstream Chunker API",
    description="Document Layout Detection & Hierarchical Chunking Service",
    lifespan=lifespan,
)

# Add CORS middleware to allow requests from any frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chunk")
async def chunk_document(file: UploadFile = File(...)):
    """
    Upload a document and return its hierarchical chunks.
    Supported formats: .txt, .pdf, .png, .jpg, .jpeg
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {sorted(SUPPORTED_EXTENSIONS)}")

    # Create a temporary file to store the uploaded content
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        # Run the pipeline with the original filename instead of the temp name
        result = pipeline.run(tmp_path, source_name=file.filename)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return {
            "status": "success",
            "document_name": file.filename,
            "layout_blocks": result["layout_block_count"],
            "chunk_count": result["chunk_count"],
            "chunks": result["chunks"]
        }
    except Exception as e:
        if tmp_path.exists():
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "arcstream-chunker"}

if __name__ == "__main__":
    import uvicorn
    import os
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(app, host=host, port=port)
