"""Tests for the PawPal+ system."""

from datetime import datetime

from pawpal_system import Pet, Task


def make_task() -> Task:
    return Task(
        task_type="feed",
        description="Morning feeding",
        scheduled_time=datetime(2026, 6, 24, 8, 0),
        priority=1,
        pet_id="pet-1",
    )


def test_mark_complete_sets_is_completed_true():
    task = make_task()
    assert task.is_completed is False

    task.mark_complete()

    assert task.is_completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Rex", species="dog", breed="Lab", age=3)
    assert len(pet.tasks) == 0

    pet.add_task(make_task())

    assert len(pet.tasks) == 1
