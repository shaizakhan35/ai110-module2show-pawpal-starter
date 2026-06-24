"""Tests for the PawPal+ system."""

from datetime import datetime, timedelta

from pawpal_system import Pet, Scheduler, Task


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


def test_sort_by_time_returns_tasks_in_chronological_order():
    pet = Pet(name="Rex", species="dog", breed="Lab", age=3)
    noon = Task(
        task_type="walk",
        description="Midday walk",
        scheduled_time=datetime(2026, 6, 24, 12, 0),
        priority=1,
        pet_id="Rex",
    )
    morning = Task(
        task_type="feed",
        description="Morning feeding",
        scheduled_time=datetime(2026, 6, 24, 8, 0),
        priority=1,
        pet_id="Rex",
    )
    evening = Task(
        task_type="feed",
        description="Evening feeding",
        scheduled_time=datetime(2026, 6, 24, 18, 0),
        priority=1,
        pet_id="Rex",
    )
    # Add out of chronological order to prove sorting does the work.
    pet.add_task(noon)
    pet.add_task(evening)
    pet.add_task(morning)
    scheduler = Scheduler(pets=[pet])

    ordered = scheduler.sort_by_time()

    assert [task.scheduled_time for task in ordered] == [
        datetime(2026, 6, 24, 8, 0),
        datetime(2026, 6, 24, 12, 0),
        datetime(2026, 6, 24, 18, 0),
    ]


def test_completing_daily_recurring_task_schedules_next_day():
    pet = Pet(name="Rex", species="dog", breed="Lab", age=3)
    task = Task(
        task_type="feed",
        description="Morning feeding",
        scheduled_time=datetime(2026, 6, 24, 8, 0),
        priority=1,
        pet_id="Rex",
        is_recurring=True,
        recurrence_days=1,
    )
    pet.add_task(task)
    scheduler = Scheduler(pets=[pet])

    next_occurrence = scheduler.complete_task(task)

    assert task.is_completed is True
    assert next_occurrence is not None
    assert next_occurrence.scheduled_time == datetime(2026, 6, 25, 8, 0)
    assert next_occurrence.is_recurring is True
    # The new occurrence is appended to the same pet's task list.
    assert next_occurrence in pet.tasks


def test_detect_conflicts_flags_same_pet_same_time():
    pet = Pet(name="Rex", species="dog", breed="Lab", age=3)
    when = datetime(2026, 6, 24, 8, 0)
    pet.add_task(
        Task(
            task_type="feed",
            description="Morning feeding",
            scheduled_time=when,
            priority=1,
            pet_id="Rex",
        )
    )
    pet.add_task(
        Task(
            task_type="walk",
            description="Morning walk",
            scheduled_time=when,
            priority=2,
            pet_id="Rex",
        )
    )
    scheduler = Scheduler(pets=[pet])

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "Rex" in warnings[0]
