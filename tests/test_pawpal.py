"""Tests for PawPal+ core behavior."""

from pawpal_system import Owner, Pet, Task, Scheduler


def test_mark_complete_changes_status():
    """Calling mark_complete() flips a task from not-done to done."""
    task = Task("Feed", due_time="08:00", duration_minutes=10, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet increases that pet's task count."""
    pet = Pet("Mochi", species="cat")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Walk", due_time="09:00", duration_minutes=20, priority="medium"))
    assert len(pet.tasks) == 1


def test_scheduler_sorts_by_priority_across_pets():
    """sort_by_priority returns tasks from all pets, highest priority first."""
    owner = Owner("Sue")
    cat = Pet("Mochi", species="cat")
    dog = Pet("Biscuit", species="dog")
    owner.add_pet(cat)
    owner.add_pet(dog)
    cat.add_task(Task("Brush", due_time="19:00", duration_minutes=15, priority="low"))
    dog.add_task(Task("Walk", due_time="08:30", duration_minutes=45, priority="high"))

    scheduler = Scheduler(owner.pets, time_budget_minutes=120)
    ordered = scheduler.sort_by_priority()

    assert [t.title for t in ordered] == ["Walk", "Brush"]


def test_sort_by_time_orders_across_pets():
    """sort_by_time returns all tasks ordered by due_time."""
    owner = Owner("Sue")
    cat = Pet("Mochi", species="cat")
    owner.add_pet(cat)
    cat.add_task(Task("Evening", due_time="19:00", duration_minutes=10, priority="low"))
    cat.add_task(Task("Morning", due_time="08:00", duration_minutes=10, priority="low"))

    scheduler = Scheduler(owner.pets, time_budget_minutes=60)
    assert [t.due_time for t in scheduler.sort_by_time()] == ["08:00", "19:00"]


def test_detect_conflicts_flags_same_time():
    """detect_conflicts warns when two tasks share the same due_time."""
    owner = Owner("Sue")
    cat = Pet("Mochi", species="cat")
    dog = Pet("Biscuit", species="dog")
    owner.add_pet(cat)
    owner.add_pet(dog)
    cat.add_task(Task("Feed", due_time="08:00", duration_minutes=10, priority="high"))
    dog.add_task(Task("Walk", due_time="08:00", duration_minutes=30, priority="high"))

    scheduler = Scheduler(owner.pets, time_budget_minutes=60)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]


def test_recurring_task_spawns_next_occurrence():
    """Completing a daily task adds a fresh uncompleted copy to the pet."""
    pet = Pet("Mochi", species="cat")
    pet.add_task(Task("Feed", due_time="08:00", duration_minutes=10, priority="high", frequency="daily"))

    pet.tasks[0].mark_complete()

    assert len(pet.tasks) == 2
    new_task = pet.tasks[1]
    assert new_task.completed is False
    assert new_task.due_date is not None


def test_build_plan_respects_time_budget():
    """build_plan schedules within the budget and skips what does not fit."""
    owner = Owner("Sue")
    dog = Pet("Biscuit", species="dog")
    owner.add_pet(dog)
    dog.add_task(Task("Walk", due_time="08:00", duration_minutes=45, priority="high"))
    dog.add_task(Task("Hike", due_time="17:00", duration_minutes=90, priority="low"))

    scheduler = Scheduler(owner.pets, time_budget_minutes=60)
    plan = scheduler.build_plan()

    assert [t.title for t in plan.scheduled] == ["Walk"]
    assert [t.title for t in plan.skipped] == ["Hike"]
    assert plan.total_minutes == 45


# --- Edge cases ------------------------------------------------------------

def test_empty_scheduler_returns_empty_plan():
    """A pet with no tasks produces an empty plan without crashing."""
    owner = Owner("Sue")
    owner.add_pet(Pet("Mochi", species="cat"))  # no tasks

    plan = Scheduler(owner.pets, time_budget_minutes=60).build_plan()

    assert plan.scheduled == []
    assert plan.skipped == []
    assert plan.total_minutes == 0


def test_no_conflict_when_times_differ():
    """detect_conflicts returns nothing when no two tasks share a time."""
    pet = Pet("Mochi", species="cat")
    pet.add_task(Task("Feed", due_time="08:00", duration_minutes=10, priority="high"))
    pet.add_task(Task("Brush", due_time="19:00", duration_minutes=10, priority="low"))

    scheduler = Scheduler([pet], time_budget_minutes=60)
    assert scheduler.detect_conflicts() == []


def test_weekly_recurrence_advances_seven_days():
    """Completing a weekly task schedules the next one 7 days out."""
    import datetime

    pet = Pet("Biscuit", species="dog")
    pet.add_task(
        Task("Bath", due_time="10:00", duration_minutes=30, priority="medium",
             frequency="weekly", due_date=datetime.date(2026, 1, 1))
    )

    pet.tasks[0].mark_complete()

    assert pet.tasks[1].due_date == datetime.date(2026, 1, 8)


def test_task_larger_than_budget_is_skipped():
    """A single task longer than the whole budget is skipped, not scheduled."""
    pet = Pet("Biscuit", species="dog")
    pet.add_task(Task("Marathon walk", due_time="08:00", duration_minutes=200, priority="high"))

    plan = Scheduler([pet], time_budget_minutes=60).build_plan()

    assert plan.scheduled == []
    assert [t.title for t in plan.skipped] == ["Marathon walk"]


def test_json_round_trip_persists_pets_and_tasks(tmp_path):
    """save_to_json then load_from_json restores owner, pets, tasks, and links."""
    import datetime

    owner = Owner("Sue")
    pet = Pet("Mochi", species="cat", breed="Tabby", age=3)
    owner.add_pet(pet)
    pet.add_task(
        Task("Feed", due_time="08:00", duration_minutes=10, priority="high",
             frequency="daily", due_date=datetime.date(2026, 1, 1))
    )

    path = tmp_path / "data.json"
    owner.save_to_json(str(path))
    loaded = Owner.load_from_json(str(path))

    assert loaded.name == "Sue"
    assert loaded.pets[0].name == "Mochi"
    task = loaded.pets[0].tasks[0]
    assert task.title == "Feed"
    assert task.due_date == datetime.date(2026, 1, 1)  # date restored, not a string
    # Bidirectional links are rebuilt on load.
    assert loaded.pets[0].owner is loaded
    assert task.pet is loaded.pets[0]
