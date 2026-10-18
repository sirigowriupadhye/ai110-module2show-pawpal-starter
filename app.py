import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

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

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

# Keep one Owner for the whole session so pets and tasks survive Streamlit reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name)
owner = st.session_state.owner
owner.name = owner_name

if st.button("Add pet"):
    if any(p.name == pet_name for p in owner.pets):
        st.warning(f"{pet_name} is already on your list.")
    else:
        owner.add_pet(Pet(pet_name, species))

if owner.pets:
    st.write("Your pets:")
    st.table([{"name": p.name, "species": p.species, "tasks": len(p.get_tasks())} for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

selected_pet_name = st.selectbox("Add task to which pet?", [p.name for p in owner.pets])

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    task_time = st.time_input("Time")

if st.button("Add task"):
    selected_pet = next((p for p in owner.pets if p.name == selected_pet_name), None)
    if selected_pet is None:
        st.warning("Add a pet first, then add tasks to it.")
    else:
        selected_pet.add_task(Task(task_title, task_time.strftime("%H:%M")))
        st.rerun()  # redraw so the "Your pets" task counts above are up to date

# Build table rows from the owner's pets so each task shows which pet it belongs to.
task_rows = [
    {
        "pet": pet.name,
        "task": task.description,
        "time": task.time,
        "frequency": task.frequency,
        "completed": task.completed,
    }
    for pet in owner.pets
    for task in pet.get_tasks()
]

if task_rows:
    st.write("Current tasks:")
    st.table(task_rows)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    # Scheduler.sort_by_time() is still a stub, so sort here ("HH:MM" sorts as text).
    tasks = sorted(scheduler.get_all_tasks(), key=lambda task: task.time)
    if tasks:
        pet_for_task = {id(task): pet.name for pet in owner.pets for task in pet.get_tasks()}
        st.success(f"Today's Schedule for {owner.name}")
        st.table(
            [
                {"time": task.time, "pet": pet_for_task[id(task)], "task": task.description}
                for task in tasks
            ]
        )
    else:
        st.warning("No tasks to schedule yet. Add one above.")
