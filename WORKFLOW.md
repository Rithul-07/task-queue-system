# How This Project Works

## The problem it solves

Some work should not make an API request wait. For example, a user might ask an
app to send an email, resize an image, create a report, or notify many people.

Instead of doing that work while the user waits, the API creates a **job**. A
worker picks up the job in the background and performs it. This project is the
system that safely manages those jobs.

## A concrete example

Imagine an app needs to send two emails:

| Job | Priority | Meaning |
| --- | ---: | --- |
| Weekly newsletter | 100 | Can wait a little |
| Password-reset email | 1 | Should be sent urgently |

Both jobs enter the queue. The password-reset email runs first because lower
numbers are more important in this project.

## The data flow

```text
1. Client sends a request
   POST /jobs
        |
        v
2. FastAPI validates the request and creates a Job
        |
        +--> PostgreSQL: permanent job record and current status
        |
        +--> Redis: lightweight priority queue entry
                       |
                       v
3. One worker claims the next available job
        |
        +--> Redis lock: prevents another worker claiming the same job
        |
        v
4. Worker performs the task
        |
        +--> success: PostgreSQL status becomes "succeeded"
        |
        +--> failure with retries left: schedule job again after a delay
        |
        +--> failure with no retries left: move it to the dead-letter queue
```

## What each part is for

| Part | Responsibility | When we add it |
| --- | --- | --- |
| FastAPI API | Receives job requests and lets users inspect or cancel jobs | Day 2 |
| `Job` model | A shared blueprint describing a job's data | Day 1 |
| PostgreSQL | Permanent source of truth: job history, payload, status, errors | Day 2 |
| Priority queue | Decides which waiting job should run next | Day 1, then Redis on Day 3 |
| Redis | Fast shared queue and temporary worker locks | Day 3 |
| Worker processes | Background programs that run the job work | Day 4 |
| Dead-letter queue | Holds jobs that repeatedly fail for later inspection | Day 4 |

## What we built on Day 1

### `app/models/job.py`

This is the **job form** or blueprint. It says every job should have an ID,
payload, priority, status, retry information, and timestamps.

It does **not** run a job or store one in a database yet. It simply ensures all
parts of the application use the same shape of data. On Day 2, PostgreSQL will
store these fields; on Day 4, a worker will update them as it executes a job.

### `app/core/priority_queue.py`

This is a small in-memory practice version of the scheduling rule. Given jobs
with different priorities, it returns the most urgent one first.

```text
queue receives:  newsletter (100), password reset (1), report (50)
queue returns:   password reset -> report -> newsletter
```

It is implemented with Python's `heapq` because it efficiently finds the next
job. The API we wrote is:

```python
queue.push("job-id", priority=10)       # add a waiting job
queue.peek()                             # inspect the next one
queue.pop()                              # claim/remove the next one
queue.update_priority("job-id", 1)      # make a job urgent
```

This local queue is **not the final production queue**. It teaches and tests
the scheduling behavior. On Day 3, Redis will hold this data so several worker
processes can safely share one queue.

## Job lifecycle

```text
pending --> running --> succeeded
   |          |
   |          +--> failed --> pending (retry after a delay)
   |                         |
   |                         +--> dead_letter (retry limit reached)
   |
   +--> cancelled
```

## Why both PostgreSQL and Redis?

- **PostgreSQL** keeps durable records. If Redis restarts, we still know every
  submitted job and its final state.
- **Redis** is optimized for quick queue operations and short-lived locks.
  It lets multiple workers coordinate without processing a job twice.

## Where we are now

At the end of Day 1, only the `Job` blueprint and local priority ordering rule
exist. There is no database, no Redis, and no background worker yet. That is
intentional: each later day adds one layer to this flow.
