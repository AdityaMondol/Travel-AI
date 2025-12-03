from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Manus Agent Platform", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class JobRequest(BaseModel):
    objective: str
    selected_agents: List[str] = ["planner", "researcher", "coder", "verifier"]
    constraints: Optional[Dict[str, Any]] = {}

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

# Routes
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "manus-backend"}

# In-memory job storage (for demo purposes)
jobs_db = {}

@app.post("/jobs", response_model=JobResponse)
async def submit_job(job: JobRequest, background_tasks: BackgroundTasks):
    job_id = f"job_{os.urandom(4).hex()}"
    logger.info(f"Job submitted: {job_id} - {job.objective}")
    
    # Store job with initial data
    jobs_db[job_id] = {
        "job_id": job_id,
        "objective": job.objective,
        "status": "processing",
        "plan": {
            "steps": [
                {
                    "id": "research_phase",
                    "agent": "researcher",
                    "instruction": "Conduct deep research on the given topic",
                    "status": "in_progress",
                    "result": None
                },
                {
                    "id": "analysis_phase",
                    "agent": "planner",
                    "instruction": "Analyze research findings and create execution plan",
                    "status": "pending",
                    "result": None
                },
                {
                    "id": "verification_phase",
                    "agent": "verifier",
                    "instruction": "Verify accuracy and completeness of results",
                    "status": "pending",
                    "result": None
                }
            ]
        },
        "logs": [
            {"timestamp": "2024-01-01T00:00:00", "agent": "system", "message": f"Job {job_id} created successfully"},
            {"timestamp": "2024-01-01T00:00:01", "agent": "planner", "message": "Initializing execution plan..."}
        ],
        "artifacts": []
    }
    
    return {"job_id": job_id, "status": "queued", "message": "Job submitted successfully"}

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs_db[job_id]

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
