

from fastapi import FastAPI


app = FastAPI(
    title="Task Queue System",
    version="0.1.0",
    description="A priority-based background job processing service.",
)

 
@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
  
    return {"status": "ok"}
