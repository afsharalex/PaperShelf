"""
FastAPI application for PaperShelf.

This module provides HTTP endpoints for interacting with the PaperShelf
application using FastAPI.
"""

import os
import uuid
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Query, Cookie, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel

from papershelf.ingest.pdf_processor import PDFProcessor
from papershelf.ingest.embedding_generator import EmbeddingGenerator
from papershelf.db.vector_store import VectorStore
from papershelf.db.chat_history import ChatHistoryDB
from papershelf.query.rag_engine import RAGEngine
from papershelf.utils.pdf_generator import generate_chat_history_pdf
from papershelf.utils.config import config


# Define request and response models
class QueryRequest(BaseModel):
    """Model for query requests."""
    query: str
    top_k: Optional[int] = 5


class QueryResponse(BaseModel):
    """Model for query responses."""
    query: str
    answer: str
    retrieved_documents: List[Dict[str, Any]]


class DocumentResponse(BaseModel):
    """Model for document responses."""
    id: str
    title: str
    author: Optional[str] = None
    page_count: Optional[int] = None
    status: str


# Create FastAPI app
app = FastAPI(
    title="PaperShelf API",
    description="API for the PaperShelf academic paper RAG system",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="papershelf/static"), name="static")

# Create global instances
pdf_processor = PDFProcessor()
embedding_generator = EmbeddingGenerator()
vector_store = VectorStore()
chat_history_db = ChatHistoryDB()
rag_engine = RAGEngine(
    vector_store=vector_store,
    embedding_generator=embedding_generator
)


# Define endpoints
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint that serves the main page."""
    return FileResponse("papershelf/static/index.html")

@app.get("/upload-page", response_class=HTMLResponse)
async def upload_page():
    """Endpoint that serves the upload form."""
    return FileResponse("papershelf/static/upload.html")

@app.get("/query-page", response_class=HTMLResponse)
async def query_page(response: Response, session_id: Optional[str] = Cookie(None)):
    """
    Endpoint that serves the query page.

    Generates a unique session ID for each new visitor and stores it in a cookie.
    """
    # If no session ID exists, create a new one
    if not session_id:
        session_id = chat_history_db.create_session()
        response.set_cookie(key="session_id", value=session_id, max_age=60*60*24*30)  # 30 days

    return FileResponse("papershelf/static/query.html")


@app.post("/upload", response_model=DocumentResponse)
async def upload_paper(file: UploadFile = File(...)):
    """
    Upload an academic paper (PDF).

    The paper will be processed, text extracted, and embeddings generated and stored.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    # Save the uploaded file temporarily
    temp_path = f"temp_{uuid.uuid4()}.pdf"
    try:
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        # Process the PDF
        metadata = pdf_processor.extract_metadata(temp_path)
        chunks = pdf_processor.process_pdf(temp_path)

        # Generate embeddings
        embeddings = embedding_generator.generate_embeddings(chunks)

        # Create document IDs
        doc_id_base = str(uuid.uuid4())
        doc_ids = [f"{doc_id_base}_{i}" for i in range(len(chunks))]

        # Create metadata for each chunk
        metadatas = []
        for i in range(len(chunks)):
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = i
            chunk_metadata["total_chunks"] = len(chunks)
            chunk_metadata["doc_id_base"] = doc_id_base
            metadatas.append(chunk_metadata)

        # Store in vector database
        vector_store.add_documents(
            document_ids=doc_ids,
            embeddings=embeddings,
            texts=chunks,
            metadatas=metadatas
        )

        return {
            "id": doc_id_base,
            "title": metadata.get("title", "Unknown"),
            "author": metadata.get("author", "Unknown"),
            "page_count": metadata.get("page_count", 0),
            "status": "success"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/query", response_model=QueryResponse)
async def query_papers(request: QueryRequest, session_id: Optional[str] = Cookie(None)):
    """
    Query the academic papers using RAG.

    The query will be processed, relevant documents retrieved, and an answer generated.
    The query and response will be saved to the database if a session ID is provided.
    """
    try:
        result = rag_engine.query(request.query)

        # Save the query and response to the database if a session ID is provided
        if session_id:
            chat_history_db.add_chat_entry(
                session_id=session_id,
                query=request.query,
                answer=result.answer,
                retrieved_documents=result.retrieved_documents
            )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying papers: {str(e)}")


@app.get("/stats")
async def get_stats():
    """Get statistics about the database."""
    try:
        stats = vector_store.get_collection_stats()
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@app.get("/sessions")
async def get_sessions():
    """Get all chat sessions."""
    try:
        sessions = chat_history_db.get_all_sessions()
        return {"sessions": sessions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting sessions: {str(e)}")


@app.get("/sessions/{session_id}")
async def get_session_history(session_id: str):
    """Get chat history for a specific session."""
    try:
        # Get session info
        session_info = chat_history_db.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        # Get chat history
        history = chat_history_db.get_session_history(session_id)

        return {
            "session_info": session_info,
            "history": history
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session history: {str(e)}")


@app.get("/sessions/{session_id}/export-pdf")
async def export_session_to_pdf(session_id: str):
    """Export chat history for a specific session to PDF."""
    try:
        # Get session info
        session_info = chat_history_db.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        # Get chat history
        history = chat_history_db.get_session_history(session_id)

        # Create PDF export directory if it doesn't exist
        os.makedirs(config.PDF_EXPORT_DIR, exist_ok=True)

        # Generate PDF
        pdf_path = generate_chat_history_pdf(config.PDF_EXPORT_DIR, session_info, history)

        # Return the PDF file
        return FileResponse(
            path=pdf_path,
            filename=os.path.basename(pdf_path),
            media_type="application/pdf"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting session to PDF: {str(e)}")


def create_app():
    """Create and configure the FastAPI application."""
    # The app is already configured in this module
    # This function is provided for compatibility with other parts of the code
    return app
