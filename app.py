import streamlit as st
from datetime import datetime

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ app — a pet care planning assistant. Add your pets,
give each one care tasks, and build a daily schedule.
"""
)

# ---------------------------------------------------------------------------
# Persistent state
# ---------------------------------------------------------------------------
# Store the Owner and Scheduler in session_state so data survives reruns.
# The Scheduler shares the Owner's `pets` list (same object), so any pet or
# task added through the Owner is automatically visible to the Scheduler.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", email="jordan@example.com")
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(pets=st.session_state.owner.pets)

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------
st.subheader("Owner")
with st.form("owner_form"):
    owner_name = st.text_input("Owner name", value=owner.name)
    owner_email = st.text_input("Owner email", value=owner.email)
    if st.form_submit_button("Save owner"):
        owner.name = owner_name
        owner.email = owner_email
        st.success(f"Owner saved: {owner.name}")

st.divider()

# ---------------------------------------------------------------------------
# Add Pet
# ---------------------------------------------------------------------------
st.subheader("Add Pet")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    breed = st.text_input("Breed", value="")
    age = st.number_input("Age (years)", min_value=0, max_value=50, value=2)
    if st.form_submit_button("Add Pet"):
        if pet_name.strip():
            owner.add_pet(Pet(name=pet_name, species=species, breed=breed, age=int(age)))
            st.success(f"Added pet: {pet_name}")
        else:
            st.error("Pet name is required.")

pets = owner.get_pets()
if pets:
    st.write("Current pets:")
    st.table(
        [
            {"name": p.name, "species": p.species, "breed": p.breed, "age": p.age,
             "tasks": len(p.get_tasks())}
            for p in pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Add Task
# ---------------------------------------------------------------------------
st.subheader("Add Task")
if not pets:
    st.info("Add a pet first, then you can assign tasks to it.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        pet_index = st.selectbox(
            "Pet",
            options=range(len(pets)),
            format_func=lambda i: pets[i].name,
        )
        task_type = st.text_input("Task type", value="walk")
        description = st.text_input("Description", value="Morning walk")
        col1, col2 = st.columns(2)
        with col1:
            task_date = st.date_input("Date", value=datetime.now().date())
        with col2:
            task_time = st.time_input("Time", value=datetime.now().time())
        priority = st.number_input(
            "Priority (1 = highest)", min_value=1, max_value=5, value=1
        )
        is_recurring = st.checkbox("Recurring")
        recurrence_days = st.multiselect(
            "Recurrence days",
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        )
        if st.form_submit_button("Add Task"):
            pet = pets[pet_index]
            pet.add_task(
                Task(
                    task_type=task_type,
                    description=description,
                    scheduled_time=datetime.combine(task_date, task_time),
                    priority=int(priority),
                    pet_id=pet.name,
                    is_recurring=is_recurring,
                    recurrence_days=recurrence_days,
                )
            )
            st.success(f"Added task '{description}' to {pet.name}")

all_tasks = scheduler.tasks
if all_tasks:
    st.write("All tasks:")
    st.table(
        [
            {
                "pet": t.pet_id,
                "type": t.task_type,
                "description": t.description,
                "time": t.scheduled_time.strftime("%Y-%m-%d %H:%M"),
                "priority": t.priority,
                "done": t.is_completed,
            }
            for t in scheduler.sort_by_time()
        ]
    )
else:
    st.info("No tasks yet.")

st.divider()

# ---------------------------------------------------------------------------
# Build Schedule
# ---------------------------------------------------------------------------
st.subheader("Build Schedule")
if st.button("Generate daily summary"):
    st.text(scheduler.show_daily_summary())

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        st.warning("Conflicting tasks (scheduled within 30 minutes for the same pet):")
        for t in conflicts:
            st.write(
                f"- {t.pet_id}: {t.task_type} at {t.scheduled_time.strftime('%H:%M')}"
            )
