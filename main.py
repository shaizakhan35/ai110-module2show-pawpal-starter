"""Demo driver for the PawPal+ system."""

from datetime import datetime

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo() -> Owner:
    """Create one owner with two pets and a few tasks scheduled today."""
    owner = Owner(name="Sam Rivera", email="sam@example.com")

    rex = Pet(name="Rex", species="dog", breed="Labrador", age=3)
    mochi = Pet(name="Mochi", species="cat", breed="Siamese", age=2)
    owner.add_pet(rex)
    owner.add_pet(mochi)

    today = datetime.now()

    def at(hour: int, minute: int = 0) -> datetime:
        return today.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # Add tasks deliberately out of chronological order to prove that
    # sort_by_time() reorders them rather than relying on insertion order.
    feed_evening = Task("Feed", "Dinner kibble", at(18, 30), 2, rex.name)
    walk_morning = Task("Walk", "Morning walk around the block", at(8, 0), 1, rex.name)
    medication = Task("Medication", "Allergy pill with treat", at(12, 15), 1, mochi.name)
    walk_evening = Task("Walk", "Evening stroll", at(20, 0), 3, rex.name)
    play = Task("Play", "Laser pointer session", at(10, 45), 2, mochi.name)
    # A daily recurring task: completing it schedules the next day's occurrence.
    daily_feed = Task(
        "Feed", "Morning kibble", at(7, 0), 1, rex.name,
        is_recurring=True, recurrence_days=1,
    )

    # Two tasks for the same pet at the same time -> a scheduling conflict.
    play_conflict = Task("Play", "Fetch in the yard", at(10, 45), 2, mochi.name)

    rex.add_task(feed_evening)
    rex.add_task(walk_morning)
    mochi.add_task(medication)
    rex.add_task(walk_evening)
    mochi.add_task(play)
    rex.add_task(daily_feed)
    mochi.add_task(play_conflict)

    # Mark a couple complete so filter_by_status() has both groups to show.
    walk_morning.mark_complete()
    medication.mark_complete()

    return owner


def print_todays_schedule(owner: Owner) -> None:
    """Print a clearly formatted schedule of today's tasks for all pets."""
    scheduler = Scheduler(pets=owner.get_pets())
    today = datetime.now()
    todays_tasks = scheduler.todays_tasks()

    width = 50
    print("=" * width)
    print(f"Today's Schedule - {today.strftime('%A, %B %d, %Y')}".center(width))
    print(f"Owner: {owner.name}".center(width))
    print("=" * width)

    if not todays_tasks:
        print("No tasks scheduled for today.")
    else:
        for task in todays_tasks:
            status = "[x]" if task.is_completed else "[ ]"
            time_str = task.scheduled_time.strftime("%I:%M %p")
            print(f"{status} {time_str}  P{task.priority}  {task.task_type} "
                  f"({task.pet_id})")
            print(f"        {task.description}")

    print("=" * width)


def _format_task(task: Task) -> str:
    """One-line representation of a task for verification output."""
    status = "[x]" if task.is_completed else "[ ]"
    time_str = task.scheduled_time.strftime("%I:%M %p")
    return f"{status} {time_str}  P{task.priority}  {task.task_type} ({task.pet_id})"


def verify_scheduler_methods(owner: Owner) -> None:
    """Print results of sort_by_time / filter_by_status / filter_by_pet."""
    scheduler = Scheduler(pets=owner.get_pets())
    width = 50

    print("\n" + "=" * width)
    print("Verifying Scheduler methods".center(width))
    print("=" * width)

    print("\nsort_by_time() - should be in chronological order:")
    for task in scheduler.sort_by_time():
        print(f"  {_format_task(task)}")

    print("\nfilter_by_status(completed=False) - pending tasks:")
    for task in scheduler.filter_by_status(completed=False):
        print(f"  {_format_task(task)}")

    print("\nfilter_by_status(completed=True) - completed tasks:")
    for task in scheduler.filter_by_status(completed=True):
        print(f"  {_format_task(task)}")

    for pet in owner.get_pets():
        print(f"\nfilter_by_pet({pet.name!r}) - tasks for {pet.name}:")
        for task in scheduler.filter_by_pet(pet.name):
            print(f"  {_format_task(task)}")

    print("=" * width)


def verify_recurring_task(owner: Owner) -> None:
    """Complete a recurring task and show its next occurrence being created."""
    scheduler = Scheduler(pets=owner.get_pets())
    width = 50

    print("\n" + "=" * width)
    print("Verifying recurring task logic".center(width))
    print("=" * width)

    # Find the daily recurring task added in build_demo().
    recurring = next(
        task for task in scheduler.tasks
        if task.is_recurring and not task.is_completed
    )

    print("\nRecurring task before completion:")
    print(f"  {_format_task(recurring)}  (repeats every {recurring.recurrence_days} day[s])")

    next_occurrence = scheduler.complete_task(recurring)

    print("\nAfter complete_task() - original is marked done:")
    print(f"  {_format_task(recurring)}")
    print("\nA new occurrence was scheduled automatically:")
    print(f"  {_format_task(next_occurrence)}")
    print("=" * width)


def verify_conflicts(owner: Owner) -> None:
    """Print any scheduling-conflict warnings detected by the scheduler."""
    scheduler = Scheduler(pets=owner.get_pets())
    width = 50

    print("\n" + "=" * width)
    print("Checking for scheduling conflicts".center(width))
    print("=" * width)

    warnings = scheduler.detect_conflicts()
    if not warnings:
        print("No conflicts found.")
    else:
        for warning in warnings:
            print(f"  ! {warning}")
    print("=" * width)


def main() -> None:
    owner = build_demo()
    print_todays_schedule(owner)
    verify_scheduler_methods(owner)
    verify_recurring_task(owner)
    verify_conflicts(owner)


if __name__ == "__main__":
    main()
