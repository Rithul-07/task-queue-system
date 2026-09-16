import asyncio
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import UTC, datetime
from app.models.job import Job, JobStatus, utc_now
from app.core.priority_queue import PriorityQueue

router = APIRouter()

# In-Memory State for Demo
job_store: Dict[str, Job] = {}
job_queue: PriorityQueue[str] = PriorityQueue()
time_queue: PriorityQueue[str] = PriorityQueue()
processed_jobs: List[Job] = []

class CreateJobRequest(BaseModel):
    payload: dict[str, Any]
    priority: int = 100
    delay_seconds: int = 0

@router.post("/jobs", response_model=Job)
def create_job(request: CreateJobRequest):
    job = Job(payload=request.payload, priority=request.priority)
    job_store[str(job.id)] = job
    
    if request.delay_seconds > 0:
        # Push to TimeHeap with the execution timestamp as the 'priority' sorting key
        execution_time = int(datetime.now(UTC).timestamp()) + request.delay_seconds
        time_queue.push(str(job.id), execution_time)
        job.status = JobStatus.PENDING # Keep as pending but it's in time heap
    else:
        # Push directly to ReadyHeap
        job_queue.push(str(job.id), job.priority)
        
    return job

@router.post("/jobs/age")
def age_jobs():
    aged = job_queue.age_priorities(decrement=5)
    # Update the job_store priorities to match the queue's new priorities
    for job_id, (pri, _) in job_queue._entries.items():
        job_store[job_id].priority = pri
    return {"message": f"Successfully aged {aged} jobs using O(n) heapify!"}

@router.get("/jobs")
def get_jobs():
    # Gather jobs from job_queue (Ready) and time_queue (Delayed)
    ready_ids = set(job_queue._entries.keys())
    delayed_ids = set(time_queue._entries.keys())
    
    pending = [job_store[jid] for jid in ready_ids if job_store[jid].status == JobStatus.PENDING]
    pending.sort(key=lambda j: (j.priority, j.created_at))
    
    delayed = [job_store[jid] for jid in delayed_ids if job_store[jid].status == JobStatus.PENDING]
    # Sort delayed by their target execution time (which is stored in the time_queue)
    delayed.sort(key=lambda j: time_queue._entries.get(str(j.id), (0,0))[0])
    
    return {
        "pending": pending,
        "delayed": delayed,
        "history": processed_jobs[-10:] # last 10 processed
    }

@router.post("/jobs/process")
async def process_next_job():
    try:
        queue_item = job_queue.pop()
    except IndexError:
        raise HTTPException(status_code=404, detail="No jobs in queue")
    
    job = job_store[queue_item.value]
    job.status = JobStatus.RUNNING
    job.updated_at = utc_now()
    
    # Simulate processing delay
    await asyncio.sleep(1)
    
    job.status = JobStatus.SUCCEEDED
    job.completed_at = utc_now()
    job.updated_at = utc_now()
    
    processed_jobs.append(job)
    
    return {"message": "Job processed", "job": job}
