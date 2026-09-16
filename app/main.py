from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
import asyncio
from datetime import UTC, datetime
from contextlib import asynccontextmanager

from app.api.endpoints import router as api_router
from app.api.endpoints import time_queue, job_queue, job_store

async def poll_time_heap():
    while True:
        await asyncio.sleep(1)
        now_ts = int(datetime.now(UTC).timestamp())
        while True:
            try:
                # Peek at the lowest timestamp in the time heap
                top_item = time_queue.peek()
                if top_item.priority <= now_ts:
                    # Time has passed, pop it
                    popped = time_queue.pop()
                    job_id = popped.value
                    # Push it into the ReadyHeap with its true priority
                    if job_id in job_store:
                        job_queue.push(job_id, job_store[job_id].priority)
                else:
                    break # The root is still in the future
            except IndexError:
                break # TimeHeap is empty

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the background task
    task = asyncio.create_task(poll_time_heap())
    yield
    # Cleanup
    task.cancel()

app = FastAPI(
    title="Task Queue System",
    version="0.1.0",
    description="A priority-based background job processing service.",
    lifespan=lifespan
)

# Ensure templates directory exists before mounting
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(templates_dir, exist_ok=True)
templates = Jinja2Templates(directory=templates_dir)

app.include_router(api_router, prefix="/api", tags=["Jobs"])

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
