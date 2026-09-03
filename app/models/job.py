

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class JobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DEAD_LETTER = "dead_letter"


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(slots=True)
class Job:
   

    payload: dict[str, Any]
    priority: int = 100
    max_retries: int = 3
    scheduled_at: datetime = field(default_factory=utc_now)
    id: UUID = field(default_factory=uuid4)
    status: JobStatus = JobStatus.PENDING
    retries: int = 0
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    completed_at: datetime | None = None
    last_error: str | None = None
