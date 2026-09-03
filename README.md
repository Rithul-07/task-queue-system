# Task Queue System

A production-oriented, priority-based job processing service built with FastAPI,
PostgreSQL, Redis, and Python.

New to task queues? Read [WORKFLOW.md](WORKFLOW.md) first for a plain-English
walkthrough and data-flow diagram.

## Current progress

Day 1 is complete: the project skeleton, domain job model, heap-backed priority
queue, and queue unit tests are in place.  Database APIs, Redis coordination,
and workers will be layered on in subsequent milestones.

## Architecture (target)

```text
Client -> FastAPI API -> PostgreSQL (job source of truth)
                     -> Redis priority queue -> Worker pool -> job execution
                                                | failures
                                                v
                                           Dead-letter queue
```

## Priority queue

`app.core.priority_queue.PriorityQueue` wraps Python's standard-library
`heapq`, which is a binary min-heap. Lower numbers run first (`0` before `100`),
and jobs with equal priority retain submission order. Insert, extract, and
priority updates are O(log n); inspection of the next job is O(1).

Updates use lazy deletion: a fresh heap entry is added and stale entries are
ignored when encountered. This is more efficient than searching a heap to
mutate an arbitrary entry.

## Local setup

Requires Python 3.11 or later.

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` for the API documentation. Currently, the
health endpoint is available at `GET /health`.

## Roadmap

1. PostgreSQL persistence and job APIs
2. Redis queue claiming and visibility timeouts
3. Worker execution, retries, and dead-letter queue
4. Authentication, rate limiting, observability, deployment, and integration tests
