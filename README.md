# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## ✨ Features

The scheduling logic lives in `Scheduler` (see `pawpal_system.py`). Implemented algorithms:

- Chronological sorting — `sort_by_time()` sorts every task by `scheduled_time`, using `priority` as the tie-breaker so same-time tasks list the most important first.
- Priority sorting — `sort_by_priority()` sorts by `priority` first, falling back to `scheduled_time` on ties.
- Filtering — `filter_by_date()` (defaults to today, accepts a `date` or `datetime`), `filter_by_pet()` (matches `Task.pet_id` to `Pet.name`), and `filter_by_status()` (pending vs. completed).
- Conflict detection — `detect_conflicts()` buckets tasks into `(pet_id, scheduled_time)` slots and flags any slot holding more than one task, returning human-readable warning strings (same pet, exact same time).
- Recurring tasks — `complete_task()` marks a task done and, if it's recurring, auto-schedules the next occurrence at `scheduled_time + recurrence_days`. `generate_recurring_tasks()` expands recurring tasks into concrete occurrences across a 7-day horizon and is idempotent (no duplicates on re-run, keyed by pet/time/type).
- Daily summary — `todays_tasks()` returns today's tasks sorted by time, and `show_daily_summary()` renders them as formatted text.

> Design note: `Scheduler` stores only `pets`; its `tasks` is a derived property (single source of truth), so any task added to a pet is automatically visible to the scheduler.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

==================================================
   Today's Schedule - Wednesday, June 24, 2026    
                Owner: Sam Rivera                 
==================================================
[ ] 08:00 AM  P1  Walk (Rex)
        Morning walk around the block
[ ] 12:15 PM  P1  Medication (Mochi)
        Allergy pill with treat
[ ] 06:30 PM  P2  Feed (Rex)
        Dinner kibble
==================================================
```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
Tests cover task completion, sorting by time, recurrence logic, and conflict detection

# Paste your pytest output here
```
====================================================================== test session starts =======================================================================
platform win32 -- Python 3.13.7, pytest-9.0.3, pluggy-1.6.0
rootdir: C:\Users\ConneXionS\Downloads\New folder (2)\ai110-module2show-pawpal-starter
plugins: anyio-4.13.0
collected 5 items                                                                                                                                                 

tests\test_pawpal.py .....                                                                                                                                  [100%]

======================================================================= 5 passed in 0.09s ========================================================================
Confidence Level: (4/5)
## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting |Scheduler.sort_by_time() |Sorts all tasks chronologically by scheduled_time|
| Filtering |Scheduler.filter_by_status(), Scheduler.filter_by_pet() | Filter by completion status or pet name |
| Conflict handling | Scheduler.detect_conflicts()| e.g., overlapping time slots |Flags tasks for the same pet at the exact same time
| Recurring tasks |Scheduler.complete_task() |Auto-generates next occurrence using timedelta|

## 🚶 Walkthrough

### Main UI features (`app.py`)

The Streamlit app is a single page with four sections:

- Owner- edit the owner's name and email; saving confirms with a success message.
- Add Pet- enter name, species, breed, and age. New pets appear in a "Current pets" table showing each pet's task count.
- Add Task- pick a pet, then set task type, description, date, time, priority (1 = highest), and optional recurrence (repeat every N days). Every task is listed in an "All tasks" table sorted chronologically via 'sort_by_time()'.
- Build Schedule- clicking the button renders today's daily summary, surfaces any conflicts as st.warning() boxes (or a success message if none), and shows the full sorted schedule in a table.

### Example workflow

1. Set the owner to Sam Rivera.
2. Add two pets: Rex(dog) and Mochi (cat).
3. Add tasks: a morning walk for Rex at 8:00, a daily recurring 7:00 feeding, allergy medication for Mochi at 12:15, and two play sessions for Mochi both at 10:45 (an intentional conflict).
4. Click Build Schedule. The schedule lists all tasks in time order, and a warning flags Mochi's 10:45 double-booking.
5. Mark the recurring feeding complete - the scheduler automatically queues tomorrow's occurrence.

### Key Scheduler behaviors

- Sorting reorders tasks by time regardless of the order they were added (priority breaks ties).
- Filtering narrows tasks by date, pet, or completion status.
- Conflict detection flags same-pet, same-time tasks with a readable warning.
- Recurring tasks reschedule themselves on completion, so a daily chore reappears for the next day.

### Sample CLI output

Run the demo driver to see these behaviors end-to-end:

```bash
python main.py
```

```text
==================================================
    Today's Schedule - Thursday, June 25, 2026
                Owner: Sam Rivera
==================================================
[ ] 07:00 AM  P1  Feed (Rex)
        Morning kibble
[x] 08:00 AM  P1  Walk (Rex)
        Morning walk around the block
[ ] 10:45 AM  P2  Play (Mochi)
        Laser pointer session
[ ] 10:45 AM  P2  Play (Mochi)
        Fetch in the yard
[x] 12:15 PM  P1  Medication (Mochi)
        Allergy pill with treat
[ ] 06:30 PM  P2  Feed (Rex)
        Dinner kibble
[ ] 08:00 PM  P3  Walk (Rex)
        Evening stroll
==================================================

==================================================
          Verifying recurring task logic
==================================================

Recurring task before completion:
  [ ] 07:00 AM  P1  Feed (Rex)  (repeats every 1 day[s])

After complete_task() - original is marked done:
  [x] 07:00 AM  P1  Feed (Rex)

A new occurrence was scheduled automatically:
  [ ] 07:00 AM  P1  Feed (Rex)
==================================================

==================================================
        Checking for scheduling conflicts
==================================================
  ! Conflict for Mochi at 2026-06-25 10:45: 'Play', 'Play' are scheduled at the same time.
==================================================
```

*(Output abbreviated — `main.py` also prints `filter_by_status()` and `filter_by_pet()` verification sections.)*
