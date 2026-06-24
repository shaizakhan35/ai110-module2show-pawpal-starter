"""PawPal+ system.

Generated from diagrams/uml.mmd.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta


@dataclass
class Task:
    task_type: str
    description: str
    scheduled_time: datetime
    priority: int
    pet_id: str
    is_recurring: bool = False
    recurrence_days: list[str] = field(default_factory=list)
    is_completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        return self.tasks

    def get_pending_tasks(self) -> list[Task]:
        """Return this pet's tasks that are not yet completed."""
        return [task for task in self.tasks if not task.is_completed]


class Owner:
    def __init__(self, name: str, email: str, pets: list[Pet] | None = None) -> None:
        """Initialize an owner with a name, email, and optional list of pets."""
        self.name = name
        self.email = email
        self.pets = pets if pets is not None else []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's list of pets."""
        self.pets.remove(pet)

    def get_pets(self) -> list[Pet]:
        """Return all pets belonging to this owner."""
        return self.pets


class Scheduler:
    def __init__(self, pets: list[Pet] | None = None) -> None:
        """Initialize the scheduler with an optional list of pets."""
        self.pets = pets if pets is not None else []

    @property
    def tasks(self) -> list[Task]:
        """Tasks derived from all pets (single source of truth)."""
        return [task for pet in self.pets for task in pet.tasks]

    def sort_by_time(self) -> list[Task]:
        """Return all tasks sorted by scheduled time, then by priority on ties."""
        return sorted(
            self.tasks,
            key=lambda task: (task.scheduled_time, task.priority),
        )

    def sort_by_priority(self) -> list[Task]:
        """Return all tasks sorted by priority, then by scheduled time on ties."""
        return sorted(
            self.tasks,
            key=lambda task: (task.priority, task.scheduled_time),
        )

    def filter_by_date(self, target: date | datetime | None = None) -> list[Task]:
        """Return tasks on the given calendar date (defaults to today).

        Accepts either a ``date`` or a ``datetime``; only the date part is used.
        """
        if target is None:
            target_date = datetime.now().date()
        elif isinstance(target, datetime):
            target_date = target.date()
        else:
            target_date = target
        return [
            task for task in self.tasks
            if task.scheduled_time.date() == target_date
        ]

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Return all tasks belonging to the pet with the given name."""
        return [task for task in self.tasks if task.pet_id == pet_name]

    def filter_by_status(self, completed: bool) -> list[Task]:
        """Return tasks matching the given completion status.

        ``completed=True`` returns finished tasks; ``completed=False`` returns
        tasks that are still pending.
        """
        return [task for task in self.tasks if task.is_completed == completed]

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of same-pet tasks scheduled within 30 minutes of each other.

        Each pair is ``(earlier, later)``. A gap of exactly 30 minutes does not
        count as a conflict.
        """
        conflicts: list[tuple[Task, Task]] = []
        # Group tasks by pet, then compare every pair for the same pet.
        for pet in self.pets:
            pet_tasks = sorted(pet.tasks, key=lambda task: task.scheduled_time)
            for i, task in enumerate(pet_tasks):
                for other in pet_tasks[i + 1:]:
                    # Tasks are time-sorted, so once one is >= 30 min away,
                    # every later task is too — stop scanning this task.
                    if other.scheduled_time - task.scheduled_time >= timedelta(minutes=30):
                        break
                    conflicts.append((task, other))
        return conflicts

    def generate_recurring_tasks(self) -> list[Task]:
        """Expand recurring tasks into concrete occurrences over the next 7 days.

        New occurrences are appended to the matching pet's task list and also
        returned. This is idempotent: re-running it will not create duplicate
        occurrences (matched by pet, time, and task type).
        """
        pets_by_id = {pet.name: pet for pet in self.pets}
        # Snapshot the source tasks and existing occurrences up front so that
        # appending new tasks below does not feed back into the loop.
        source_tasks = [
            task for task in self.tasks
            if task.is_recurring and task.recurrence_days
        ]
        existing = {
            (task.pet_id, task.scheduled_time, task.task_type)
            for task in self.tasks
        }
        generated: list[Task] = []
        for task in source_tasks:
            target_days = {day.lower() for day in task.recurrence_days}
            # Expand across the next 7 days, including the original day.
            for offset in range(0, 7):
                occurrence_time = task.scheduled_time + timedelta(days=offset)
                if occurrence_time.strftime("%A").lower() not in target_days:
                    continue
                key = (task.pet_id, occurrence_time, task.task_type)
                if key in existing:
                    continue
                existing.add(key)
                new_task = Task(
                    task_type=task.task_type,
                    description=task.description,
                    scheduled_time=occurrence_time,
                    priority=task.priority,
                    pet_id=task.pet_id,
                    is_recurring=False,
                    recurrence_days=[],
                )
                generated.append(new_task)
                pet = pets_by_id.get(task.pet_id)
                if pet is not None:
                    pet.add_task(new_task)
        return generated

    def todays_tasks(self) -> list[Task]:
        """Return today's tasks sorted by time (priority breaks ties)."""
        todays = self.filter_by_date()
        todays.sort(key=lambda task: (task.scheduled_time, task.priority))
        return todays

    def show_daily_summary(self) -> str:
        """Return a formatted text summary of today's tasks."""
        today = datetime.now()
        todays_tasks = self.todays_tasks()
        header = f"Daily Summary for {today.strftime('%Y-%m-%d')}"
        if not todays_tasks:
            return f"{header}\nNo tasks scheduled for today."
        lines = [header]
        for task in todays_tasks:
            status = "done" if task.is_completed else "pending"
            time_str = task.scheduled_time.strftime("%H:%M")
            lines.append(
                f"[{status}] {time_str} - {task.task_type}: "
                f"{task.description} (pet {task.pet_id}, priority {task.priority})"
            )
        return "\n".join(lines)
