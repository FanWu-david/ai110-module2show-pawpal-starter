from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name, contact_info="")

st.divider()

st.subheader("Add a Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
breed = st.text_input("Breed", value="")

if st.button("Add pet"):
    st.session_state.owner.add_pet(Pet(name=pet_name, species=species, breed=breed))

pets = st.session_state.owner.get_pets()
if pets:
    st.write("Current pets:")
    st.table([pet.get_info() for pet in pets])
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Add a Task")

if pets:
    pets_by_id = {pet.pet_id: pet for pet in pets}
    selected_pet_id = st.selectbox(
        "Pet", options=list(pets_by_id.keys()), format_func=lambda pid: pets_by_id[pid].name
    )
    selected_pet = pets_by_id[selected_pet_id]

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    col4, col5 = st.columns(2)
    with col4:
        category = st.selectbox("Category", ["walk", "feeding", "meds", "grooming", "enrichment", "other"])
    with col5:
        preferred_time = st.time_input("Preferred time", value=time(8, 0))

    if st.button("Add task"):
        selected_pet.add_task(
            Task(
                title=task_title,
                category=category,
                duration_minutes=int(duration),
                priority=priority,
                preferred_time=preferred_time,
            )
        )

    all_tasks = st.session_state.owner.get_all_tasks()
    if all_tasks:
        st.write("Current tasks:")
        st.table(
            [
                {
                    "pet": pets_by_id[task.pet_id].name if task.pet_id in pets_by_id else "?",
                    "title": task.title,
                    "category": task.category,
                    "duration_minutes": task.duration_minutes,
                    "priority": task.priority,
                    "preferred_time": task.preferred_time,
                }
                for task in all_tasks
            ]
        )
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("Add a pet before adding tasks.")

st.divider()

st.subheader("Build Schedule")
available_time = st.number_input("Available time today (minutes)", min_value=1, max_value=600, value=120)

if st.button("Generate schedule"):
    scheduler = Scheduler(available_time_minutes=int(available_time))
    plan = scheduler.generate_daily_plan(st.session_state.owner)
    st.text(scheduler.explain_plan(plan))
