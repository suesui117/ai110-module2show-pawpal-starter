import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan daily pet care tasks across all your pets.")

# --- Application memory -----------------------------------------------------
# Streamlit re-runs this script on every interaction, so we keep the Owner
# (and all its pets/tasks) in st.session_state so the data persists.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")

owner = st.session_state.owner

# --- Owner -----------------------------------------------------------------
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

st.divider()

# --- Add a pet -------------------------------------------------------------
st.subheader("Add a pet")
with st.form("add_pet", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    breed = st.text_input("Breed (optional)", value="")
    age = st.number_input("Age (optional)", min_value=0, max_value=40, value=0)
    if st.form_submit_button("Add pet") and pet_name.strip():
        owner.add_pet(
            Pet(pet_name.strip(), species, breed=breed or None, age=age or None)
        )
        st.success(f"Added {pet_name.strip()}!")

if not owner.pets:
    st.info("No pets yet. Add one above to get started.")

st.divider()

# --- Add a task to a pet ---------------------------------------------------
if owner.pets:
    st.subheader("Add a task")
    with st.form("add_task", clear_on_submit=True):
        pet_names = [p.name for p in owner.pets]
        chosen = st.selectbox("For which pet?", pet_names)
        title = st.text_input("Task title", value="")
        due_time = st.text_input("Due time (HH:MM)", value="08:00")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        if st.form_submit_button("Add task") and title.strip():
            pet = owner.pets[pet_names.index(chosen)]
            pet.add_task(Task(title.strip(), due_time, int(duration), priority))
            st.success(f"Added '{title.strip()}' for {chosen}!")

    # --- Current pets & tasks ----------------------------------------------
    st.subheader("Current pets & tasks")
    for pet in owner.pets:
        with st.expander(f"{pet.name} ({pet.species}) — {len(pet.tasks)} task(s)", expanded=True):
            if pet.tasks:
                st.table(
                    [
                        {
                            "task": t.title,
                            "due_time": t.due_time,
                            "duration_minutes": t.duration_minutes,
                            "priority": t.priority,
                            "completed": t.completed,
                        }
                        for t in pet.list_tasks()
                    ]
                )
            else:
                st.caption("No tasks yet.")

    st.divider()

    # --- Generate the daily plan -------------------------------------------
    st.subheader("Build today's schedule")
    budget = st.number_input(
        "Time budget for today (minutes)", min_value=5, max_value=1440, value=60, step=5
    )
    if st.button("Generate schedule"):
        scheduler = Scheduler(owner.pets, time_budget_minutes=int(budget))
        plan = scheduler.build_plan()
        if plan.to_table():
            st.markdown(f"**{plan.total_minutes} min scheduled** of {int(budget)} min budget")
            st.table(plan.to_table())
            st.text(plan.explain())
        else:
            st.warning("No tasks to schedule. Add some tasks first.")
