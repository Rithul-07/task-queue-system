import pytest

from app.core.priority_queue import PriorityQueue


def test_pop_returns_lowest_priority_number_first() -> None:
    queue: PriorityQueue[str] = PriorityQueue()
    queue.push("background", priority=100)
    queue.push("urgent", priority=1)
    queue.push("normal", priority=50)

    assert queue.pop().value == "urgent"
    assert queue.pop().value == "normal"
    assert queue.pop().value == "background"


def test_equal_priorities_preserve_submission_order() -> None:
    queue: PriorityQueue[str] = PriorityQueue()
    queue.push("first", priority=10)
    queue.push("second", priority=10)

    assert queue.pop().value == "first"
    assert queue.pop().value == "second"


def test_update_priority_changes_next_item() -> None:
    queue: PriorityQueue[str] = PriorityQueue()
    queue.push("normal", priority=50)
    queue.push("later", priority=100)
    queue.update_priority("later", priority=5)

    next_item = queue.pop()
    assert next_item.value == "later"
    assert next_item.priority == 5


def test_multiple_updates_do_not_reactivate_stale_entries() -> None:
    queue: PriorityQueue[str] = PriorityQueue()
    queue.push("job-1", priority=10)
    queue.push("job-2", priority=10)
    queue.update_priority("job-1", priority=5)
    queue.update_priority("job-1", priority=10)

    assert queue.pop().value == "job-2"
    assert queue.pop().value == "job-1"


def test_duplicate_and_unknown_items_are_rejected() -> None:
    queue: PriorityQueue[str] = PriorityQueue()
    queue.push("job-1", priority=10)

    with pytest.raises(ValueError):
        queue.push("job-1", priority=20)
    with pytest.raises(KeyError):
        queue.update_priority("missing", priority=1)


def test_pop_empty_queue_raises_index_error() -> None:
    with pytest.raises(IndexError, match="empty"):
        PriorityQueue[str]().pop()
