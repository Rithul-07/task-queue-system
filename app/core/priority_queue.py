

from __future__ import annotations

import heapq
from dataclasses import dataclass
from itertools import count
from typing import Generic, Hashable, TypeVar


ItemT = TypeVar("ItemT", bound=Hashable)


@dataclass(frozen=True, slots=True)
class QueueItem(Generic[ItemT]):
    """An item returned when a job is claimed from the queue."""

    value: ItemT
    priority: int


class PriorityQueue(Generic[ItemT]):
    
    

    def __init__(self) -> None:
        self._heap: list[tuple[int, int, int, ItemT]] = []
        self._entries: dict[ItemT, tuple[int, int]] = {}
        self._sequence = count()
        self._version = count()

    def __len__(self) -> int:
        return len(self._entries)

    def __bool__(self) -> bool:
        return bool(self._entries)

    def push(self, value: ItemT, priority: int) -> None:
        """Add ``value`` at ``priority``; values must be unique."""
        if value in self._entries:
            raise ValueError(f"item already exists in queue: {value!r}")
        self._add(value, priority)

    def pop(self) -> QueueItem[ItemT]:
        """Remove and return the lowest-priority-number item."""
        while self._heap:
            priority, _, version, value = heapq.heappop(self._heap)
            if self._entries.get(value) == (priority, version):
                del self._entries[value]
                return QueueItem(value=value, priority=priority)
        raise IndexError("pop from an empty priority queue")

    def peek(self) -> QueueItem[ItemT]:
        """Return the next item without removing it."""
        while self._heap:
            priority, _, version, value = self._heap[0]
            if self._entries.get(value) == (priority, version):
                return QueueItem(value=value, priority=priority)
            heapq.heappop(self._heap)
        raise IndexError("peek from an empty priority queue")

    def update_priority(self, value: ItemT, priority: int) -> None:
        """Change an existing item's priority in O(log n)."""
        if value not in self._entries:
            raise KeyError(f"item is not in queue: {value!r}")
        self._add(value, priority)

    def _add(self, value: ItemT, priority: int) -> None:
        version = next(self._version)
        self._entries[value] = (priority, version)
        heapq.heappush(self._heap, (priority, next(self._sequence), version, value))

    def age_priorities(self, decrement: int = 1) -> int:
        """
        O(n) Starvation Prevention algorithm.
        Decreases the priority number (increases actual priority) of all waiting items,
        and restructures the binary heap in O(n) time using heapify.
        Returns the number of items aged.
        """
        if not self._entries:
            return 0
            
        new_heap = []
        aged_count = 0
        
        # We only keep valid items (lazy deletion cleanup happens here too!)
        for priority, seq, version, value in self._heap:
            if self._entries.get(value) == (priority, version):
                # Age the priority (floor at 0)
                new_priority = max(0, priority - decrement)
                # Update the entries dictionary
                self._entries[value] = (new_priority, version)
                new_heap.append((new_priority, seq, version, value))
                aged_count += 1
                
        self._heap = new_heap
        heapq.heapify(self._heap)
        return aged_count
