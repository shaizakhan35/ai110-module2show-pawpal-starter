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

    rex.add_task(
        Task(
            task_type="Walk",
            description="Morning walk around the block",
            scheduled_time=today.replace(hour=8, minute=0, second=0, microsecond=0),
            priority=1,
            pet_id=rex.name,
        )
    )
    rex.add_task(
        Task(
            task_type="Feed",
            description="Dinner kibble",
            scheduled_time=today.replace(hour=18, minute=30, second=0, microsecond=0),
            priority=2,
            pet_id=rex.name,
        )
    )
    mochi.add_task(
        Task(
            task_type="Medication",
            description="Allergy pill with treat",
            scheduled_time=today.replace(hour=12, minute=15, second=0, microsecond=0),
            priority=1,
            pet_id=mochi.name,
        )
    )

    return owner


def print_todays_schedule(owner: Owner) -> None:
    """Print a clearly formatted schedule of today's tasks for all pets."""
    scheduler = Scheduler(pets=owner.get_pets())
    today = datetime.now()
    todays_tasks = scheduler.filter_by_date(today)
    todays_tasks.sort(key=lambda task: task.scheduled_time)

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


def main() -> None:
    owner = build_demo()
    print_todays_schedule(owner)


if __name__ == "__main__":
    main()
