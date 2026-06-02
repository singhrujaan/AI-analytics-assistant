# project/app.py
#
# FastAPI web server for the AI Analytics Assistant.
# Two endpoints:
# 1. POST /upload  — upload a CSV file
# 2. POST /ask     — ask a question about the uploaded file

import os
import sys
sys.path.append('project')

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import shutil

from agent import run_agent

# Create the FastAPI app
app = FastAPI(
    title="AI Analytics Assistant",
    description="Upload a CSV and ask questions about it in plain English",
    version="1.0.0"
)
# Add this import at the top of the file
from fastapi.middleware.cors import CORSMiddleware

# Add this right after app = FastAPI(...)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # allow all origins for development
    allow_methods=["*"],      # allow all HTTP methods
    allow_headers=["*"],      # allow all headers
)

# Store the path of the currently uploaded file
current_file_path = ""


# ── Pydantic models ──
# Define the shape of requests and responses

class QuestionRequest(BaseModel):
    question: str          # what the user wants to know

class AnalysisResponse(BaseModel):
    answer: str            # Claude's plain English answer
    steps: int             # how many agent steps were taken
    charts: list           # paths to any generated charts
    question: str          # echo back the question


# ════════════════════════════════════
# ENDPOINT 1 — Upload CSV
# ════════════════════════════════════

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a CSV file for analysis.
    Saves the file to project/data/ folder.
    """
    global current_file_path

    # Only accept CSV files
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are accepted"
        )

    # Save the uploaded file
    save_path = f"project/data/{file.filename}"
    os.makedirs("project/data", exist_ok=True)

    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Remember the file path for analysis
    current_file_path = save_path

    return {
        "message": f"File uploaded successfully",
        "filename": file.filename,
        "path": save_path
    }


# ════════════════════════════════════
# ENDPOINT 2 — Ask a Question
# ════════════════════════════════════

@app.post("/ask", response_model=AnalysisResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about the uploaded dataset.
    The agent analyses the data and returns an answer.
    """
    global current_file_path

    # Make sure a file has been uploaded
    if not current_file_path:
        raise HTTPException(
            status_code=400,
            detail="No file uploaded. Please upload a CSV file first using /upload"
        )

    # Make sure the file still exists
    if not os.path.exists(current_file_path):
        raise HTTPException(
            status_code=404,
            detail="Uploaded file not found. Please upload again."
        )

    # Run the agent
    result = run_agent(
        question=request.question,
        filepath=current_file_path
    )

    return AnalysisResponse(
        answer=result["answer"],
        steps=result["steps"],
        charts=result["charts"],
        question=request.question
    )


# ════════════════════════════════════
# ENDPOINT 3 — Get a Chart
# ════════════════════════════════════

@app.get("/chart/{filename}")
async def get_chart(filename: str):
    """
    Returns a generated chart image by filename.
    """
    chart_path = f"project/charts/{filename}"

    if not os.path.exists(chart_path):
        raise HTTPException(status_code=404, detail="Chart not found")

    return FileResponse(chart_path)


# ════════════════════════════════════
# HEALTH CHECK
# ════════════════════════════════════

@app.get("/")
async def health_check():
    """Check the API is running."""
    return {
        "status": "running",
        "message": "AI Analytics Assistant is ready",
        "endpoints": ["/upload", "/ask", "/chart/{filename}"]
    }