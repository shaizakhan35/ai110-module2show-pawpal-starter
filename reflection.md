# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
My initial UML design included four classes. Owner holds owner identity and maintains a collection of pets. Pet represents a single animal with attributes like breed and age, and keeps its own list of tasks. Task is a dataclass for a single care event and it stores what the task is, when it's scheduled, its priority, and whether it recurs. Scheduler is the central coordinator that holds all tasks and pets and exposes the algorithmic methods for sorting, filtering, conflict detection, and recurring task generation.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

The AI flagged two problems.
Change 1: Task had no way to identify its pet. I added pet_id: str to Task. Now detect_conflicts() and show_daily_summary() can group tasks by pet.
Change 2: Scheduler kept its own tasks list separate from Pet.tasks. This meant two copies of the same data that could drift out of sync. I replaced it with a property that flattens tasks from all pets. Now pets are the single source of truth.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?
My scheduler looks at two things: when a task is scheduled and how urgent it is. I made time the main constraint because pet care tasks like medications and walks have to happen at specific times. Priority helps when tasks could fit in the same slot.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler only flags tasks scheduled at the exact same time and it does not detect overlapping durations. For example, a 30-minute walk starting at 8:00 and a feeding at 8:15 would not be flagged as a conflict. This tradeoff is reasonable because tasks in this app don't have a duration field and exact-time matching is simpler to implement and easier to understand. Adding duration-based overlap detection would require storing task length and comparing time ranges, which adds complexity not needed for a basic pet care schedule.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?
I used AI for almost everything that was repetitive including writing the class skeletons and adding docstrings. The prompts that worked best were the specific ones where I attached my actual file and said exactly what I wanted changed. Vague prompts like "improve this" gave vague answers. Specific prompts like "add pet_id to Task and explain why" gave useful ones.


**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
The AI rewrote my conflict detection from a 30-minute overlap check to exact same-time matching. The new version was shorter and easier to read so I kept it, but I didn't just accept it blindly, I ran the demo script to make sure it still caught the conflict. I set up in main.py, then wrote down the tradeoff in section 2b so it was clear I knew what changed and why.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?
I tested the five behaviors most likely to break quietly: marking a task complete, adding a task to a pet, sorting by time, generating the next occurrence of a recurring task, and flagging a scheduling conflict. These mattered because the whole app depends on them as if sorting is broken the schedule looks wrong, if recurrence is broken tasks just disappear after completion.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?
I'd say 4 out of 5. Everything passes and the app runs without errors. The gaps are edge cases I haven't tested yet like what happens with a pet that has no tasks, or a recurring task that lands on the last day of the month, or two pets with the same name confusing the pet_id lookup.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
The part I'm most satisfied with is the CLI demo script. Before touching the UI I had a working schedule printing cleanly in the terminal, which made the Streamlit part way less stressful because I already knew the logic worked.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I'd add task duration. Right now every task is just a point in time with no length, which means conflict detection can't catch a 45-minute walk overlapping with a feeding 20 minutes later. That's the biggest gap between what the app does and what would actually be useful.


**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
The biggest thing I learned is that AI is great at writing code but bad at making design decisions. It generated my skeletons and docstrings faster than I ever could have, but every time it made a structural choice like removing the 30-minute conflict window I had to catch it, and decide whether it was actually right for my design. Being the lead architect means you can't just accept output, you have to know your system well enough to evaluate it.
