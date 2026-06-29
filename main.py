"""PawPal+ demo script (CLI testing ground).

Builds a small owner/pet/task setup and exercises the scheduler: sorting,
filtering, conflict detection, recurring tasks, and the daily plan.
Run with:  python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def build_demo_owner() -> Owner:
    """Create one owner with two pets and several tasks (added out of order)."""
    owner = Owner("Sue")

    mochi = Pet("Mochi", species="cat", breed="Tabby", age=3)
    biscuit = Pet("Biscuit", species="dog", breed="Golden Retriever", age=5)
    owner.add_pet(mochi)
    owner.add_pet(biscuit)

    # Deliberately added out of time order to prove sort_by_time() works.
    mochi.add_task(Task("Evening brushing", "19:00", 15, "low"))
    mochi.add_task(Task("Morning feeding", "08:00", 10, "high", frequency="daily"))
    biscuit.add_task(Task("Long hike", "17:00", 90, "low"))
    biscuit.add_task(Task("Morning walk", "08:00", 45, "high"))  # same time as feeding!
    biscuit.add_task(Task("Medication", "09:00", 5, "medium"))

    return owner


def main() -> None:
    owner = build_demo_owner()
    scheduler = Scheduler(owner.pets, time_budget_minutes=60)

    print(f"PawPal+ — Today's Schedule for {owner.name}")
    print(f"Pets: {', '.join(p.name for p in owner.pets)}")
    print("=" * 55)

    # 1. Sorting by time (tasks were added out of order).
    print("\n[Sorted by time]")
    for t in scheduler.sort_by_time():
        print(f"  {t.due_time}  {t.title} ({t.pet.name})")

    # 2. Filtering by pet.
    print("\n[Filter by pet: Biscuit]")
    for t in scheduler.filter_by_pet("Biscuit"):
        print(f"  {t.due_time}  {t.title}")

    # 3. Conflict detection (two 08:00 tasks).
    print("\n[Conflict detection]")
    conflicts = scheduler.detect_conflicts()
    for w in conflicts or ["  None"]:
        print(f"  {w}")

    # 4. Recurring tasks: completing a daily task spawns tomorrow's copy.
    print("\n[Recurring tasks]")
    feeding = next(t for t in owner.all_tasks() if t.frequency == "daily")
    before = len(owner.all_tasks())
    feeding.mark_complete()
    after = len(owner.all_tasks())
    print(f"  Completed '{feeding.title}' (daily) -> task count {before} to {after}")
    new_copy = next(
        t for t in feeding.pet.tasks if not t.completed and t.title == feeding.title
    )
    print(f"  Next occurrence scheduled for: {new_copy.due_date}")

    # 5. The daily plan (filters completed, sorts by priority, fits budget).
    print("\n[Today's plan]")
    plan = scheduler.build_plan()
    print(plan.explain())


if __name__ == "__main__":
    main()
