"""PawPal+ system skeleton.

Generated from diagrams/uml.mmd. Method bodies are stubs only.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta


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
        """Return all tasks sorted by their scheduled time."""
        return sorted(self.tasks, key=lambda task: task.scheduled_time)

    def sort_by_priority(self) -> list[Task]:
        """Return all tasks sorted by priority."""
        return sorted(self.tasks, key=lambda task: task.priority)

    def filter_by_date(self, date: datetime) -> list[Task]:
        """Return tasks scheduled on the same calendar date as the given date."""
        return [
            task for task in self.tasks
            if task.scheduled_time.date() == date.date()
        ]

    def detect_conflicts(self) -> list[Task]:
        """Return tasks for the same pet scheduled within 30 minutes of each other."""
        conflicts: list[Task] = []
        # Group tasks by pet, then compare every pair for the same pet.
        for pet in self.pets:
            pet_tasks = sorted(pet.tasks, key=lambda task: task.scheduled_time)
            for i, task in enumerate(pet_tasks):
                for other in pet_tasks[i + 1:]:
                    gap = abs(other.scheduled_time - task.scheduled_time)
                    if gap < timedelta(minutes=30):
                        if task not in conflicts:
                            conflicts.append(task)
                        if other not in conflicts:
                            conflicts.append(other)
        return conflicts

    def generate_recurring_tasks(self) -> list[Task]:
        """Expand recurring tasks into concrete occurrences over the next 7 days."""
        weekday_names = [
            "Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday",
        ]
        generated: list[Task] = []
        for task in self.tasks:
            if not task.is_recurring or not task.recurrence_days:
                continue
            target_days = {day.lower() for day in task.recurrence_days}
            # Expand into the next 7 days following the original scheduled time.
            for offset in range(1, 8):
                occurrence_time = task.scheduled_time + timedelta(days=offset)
                if weekday_names[occurrence_time.weekday()].lower() in target_days:
                    generated.append(
                        Task(
                            task_type=task.task_type,
                            description=task.description,
                            scheduled_time=occurrence_time,
                            priority=task.priority,
                            pet_id=task.pet_id,
                            is_recurring=False,
                            recurrence_days=[],
                        )
                    )
        return generated

    def show_daily_summary(self) -> str:
        """Return a formatted text summary of today's tasks."""
        today = datetime.now()
        todays_tasks = self.filter_by_date(today)
        todays_tasks.sort(key=lambda task: task.scheduled_time)
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
