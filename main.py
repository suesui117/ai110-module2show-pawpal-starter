"""PawPal+ demo script (CLI testing ground).

Builds a small owner/pet/task setup and prints today's schedule using the
Scheduler. Run with:  python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def build_demo_owner() -> Owner:
    """Create one owner with two pets and several tasks."""
    owner = Owner("Sue")

    mochi = Pet("Mochi", species="cat", breed="Tabby", age=3)
    biscuit = Pet("Biscuit", species="dog", breed="Golden Retriever", age=5)
    owner.add_pet(mochi)
    owner.add_pet(biscuit)

    # Tasks span both pets, with different times and priorities.
    mochi.add_task(Task("Morning feeding", due_time="08:00", duration_minutes=10, priority="high"))
    mochi.add_task(Task("Evening brushing", due_time="19:00", duration_minutes=15, priority="low"))
    biscuit.add_task(Task("Morning walk", due_time="08:30", duration_minutes=45, priority="high"))
    biscuit.add_task(Task("Medication", due_time="09:00", duration_minutes=5, priority="medium"))
    biscuit.add_task(Task("Long hike", due_time="17:00", duration_minutes=90, priority="low"))

    return owner


def main() -> None:
    owner = build_demo_owner()

    print(f"PawPal+ — Today's Schedule for {owner.name}")
    print(f"Pets: {', '.join(p.name for p in owner.pets)}")
    print(f"Total tasks across all pets: {len(owner.all_tasks())}")
    print("-" * 50)

    # The Scheduler is the brain: it organizes tasks across BOTH pets and
    # builds a plan that fits a daily time budget.
    scheduler = Scheduler(owner.pets, time_budget_minutes=60)
    plan = scheduler.build_plan()

    print(plan.explain())


if __name__ == "__main__":
    main()
