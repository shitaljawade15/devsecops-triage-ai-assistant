# =====================================================================
# 🚀 FASTAPI BACKEND: MULTI-TENANT DEVSECOPS COPILOT
# =====================================================================

import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from qdrant_client.models import FieldCondition, Filter, MatchValue, PointStruct

from config import COLLECTION_NAME, TRAINED_MODEL_ID
from database import initialize_database, qdrant
from services import (
    chunk_text,
    enhance_query,
    extract_text_from_file,
    get_embedding,
    query_trained_model,
)
import storage


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    storage.init_db()
    yield
    print("🛑 Shutting down server...")


app = FastAPI(
    title="Secure Software Delivery Assistant",
    description="Multi-tenant, thread-isolated DevSecOps AI assistant.",
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic Data Models ---
class ChatRequest(BaseModel):
    username: str = Field(..., description="Active user ID/username")
    thread_id: str = Field(..., description="Isolated project/thread ID")
    question: str = Field(..., description="Developer inquiry or security question")
    top_k: int = Field(default=3, ge=1, le=5, description="Number of context chunks to retrieve")


class ChatResponse(BaseModel):
    question: str
    answer: str
    sources_used: list[str]
    model_used: str


class FileUploadResponse(BaseModel):
    filename: str
    file_type: str
    chunks_indexed: int
    thread_id: str
    status: str


# --- Endpoints ---
@app.post("/upload-file", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    username: str = Form(...),
    thread_id: str = Form(...)
):
    """
    Receives scan/policy files, parses any format, generates 768-dim embeddings,
    and tags each vector point with thread_id & username for tenant isolation.
    """
    try:
        file_bytes = await file.read()
        full_text = extract_text_from_file(file.filename, file_bytes)

        if not full_text:
            raise HTTPException(status_code=400, detail="Uploaded file contains no readable text.")

        chunks = chunk_text(full_text)[:30]

        points = []
        for chunk in chunks:
            vector = get_embedding(chunk)
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "text": chunk,
                    "source_file": file.filename,
                    "username": username,
                    "thread_id": thread_id,  # 🔒 Tenant isolation key
                }
            )
            points.append(point)

        qdrant.upsert(collection_name=COLLECTION_NAME, points=points)

        file_ext = file.filename.split(".")[-1].upper() if "." in file.filename else "TXT"

        return FileUploadResponse(
            filename=file.filename,
            file_type=file_ext,
            chunks_indexed=len(points),
            thread_id=thread_id,
            status="File vectorized and stored securely under this thread."
        )

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
def chat_with_assistant(payload: ChatRequest):
    """
    Enhances query, retrieves context STRICTLY filtered by thread_id,
    and prompts the fine-tuned security model.
    """
    # 1. Enhance query with DevSecOps keywords
    search_query = enhance_query(payload.question)

    # 2. Vectorize the enhanced query
    query_vector = get_embedding(search_query)

    # 3. Retrieve chunks with Qdrant metadata filter (prevents cross-project leakage)
    thread_filter = Filter(
        must=[
            FieldCondition(key="thread_id", match=MatchValue(value=payload.thread_id))
        ]
    )

    search_results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=thread_filter,
        limit=payload.top_k
    )

    matched_texts = [p.payload["text"] for p in search_results.points]
    context_block = "\n---\n".join(matched_texts) if matched_texts else "No uploaded documents found for this specific thread."

    # 4. Generate grounded triage decision using fine-tuned model
    generated_answer = query_trained_model(payload.question, context_block)

    return ChatResponse(
        question=payload.question,
        answer=generated_answer,
        sources_used=matched_texts,
        model_used=TRAINED_MODEL_ID
    )