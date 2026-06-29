"""PawPal+ logic layer.

Core classes (from diagrams/uml.mmd) plus the "smarter scheduling" algorithms:
sorting, filtering, recurring tasks, and conflict detection. Data-holding
objects use dataclasses to stay clean.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, timedelta


@dataclass(eq=False)
class Task:
    """A single care activity for one pet."""

    title: str
    due_time: str                 # e.g. "08:00"
    duration_minutes: int
    priority: str                 # "low" | "medium" | "high"
    completed: bool = False
    pet: "Pet | None" = None
    frequency: str = "none"       # "none" | "daily" | "weekly"
    due_date: date | None = None  # used to advance recurring tasks

    def mark_complete(self) -> None:
        """Mark this task done; if recurring, spawn the next occurrence."""
        self.completed = True
        if self.frequency in ("daily", "weekly") and self.pet is not None:
            self.pet.add_task(self.next_occurrence())

    def next_occurrence(self) -> "Task":
        """Return a fresh, uncompleted copy of this task on its next date."""
        step = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)
        base = self.due_date or date.today()
        return Task(
            title=self.title,
            due_time=self.due_time,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            due_date=base + step,
        )

    def priority_rank(self) -> int:
        """Return a sortable number for this task's priority (higher = more urgent)."""
        ranks = {"high": 3, "medium": 2, "low": 1}
        return ranks.get(self.priority.lower(), 0)

    def to_dict(self) -> dict:
        """Serialize this task to a plain dict (the pet link is omitted)."""
        return {
            "title": self.title,
            "due_time": self.due_time,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "completed": self.completed,
            "frequency": self.frequency,
            "due_date": self.due_date.isoformat() if self.due_date else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Rebuild a Task from a dict produced by to_dict()."""
        due_date = data.get("due_date")
        return cls(
            title=data["title"],
            due_time=data["due_time"],
            duration_minutes=data["duration_minutes"],
            priority=data["priority"],
            completed=data.get("completed", False),
            frequency=data.get("frequency", "none"),
            due_date=date.fromisoformat(due_date) if due_date else None,
        )


@dataclass(eq=False)
class Pet:
    """A single pet. Holds identifying info and its own care tasks."""

    name: str
    species: str
    breed: str | None = None
    age: int | None = None
    owner: "Owner | None" = None
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet and link the task back to this pet."""
        task.pet = self
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet (by identity)."""
        self.tasks = [t for t in self.tasks if t is not task]

    def list_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        return self.tasks

    def to_dict(self) -> dict:
        """Serialize this pet and its tasks to a plain dict (owner link omitted)."""
        return {
            "name": self.name,
            "species": self.species,
            "breed": self.breed,
            "age": self.age,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        """Rebuild a Pet (and its tasks) from a dict produced by to_dict()."""
        pet = cls(
            name=data["name"],
            species=data["species"],
            breed=data.get("breed"),
            age=data.get("age"),
        )
        for task_data in data.get("tasks", []):
            pet.add_task(Task.from_dict(task_data))  # add_task relinks task.pet
        return pet


@dataclass(eq=False)
class Owner:
    """A pet owner. Holds identity and the pets they own."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner and link the pet back to this owner."""
        pet.owner = self
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner (by identity)."""
        self.pets = [p for p in self.pets if p is not pet]

    def all_tasks(self) -> list[Task]:
        """Provide access to every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def to_dict(self) -> dict:
        """Serialize this owner and all pets/tasks to a plain dict."""
        return {"name": self.name, "pets": [pet.to_dict() for pet in self.pets]}

    @classmethod
    def from_dict(cls, data: dict) -> "Owner":
        """Rebuild an Owner (with pets and tasks) from a dict."""
        owner = cls(name=data["name"])
        for pet_data in data.get("pets", []):
            owner.add_pet(Pet.from_dict(pet_data))  # add_pet relinks pet.owner
        return owner

    def save_to_json(self, path: str = "data.json") -> None:
        """Write this owner's full state (pets + tasks) to a JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_json(cls, path: str = "data.json") -> "Owner":
        """Load an Owner from a JSON file written by save_to_json()."""
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


@dataclass
class Plan:
    """The result of scheduling: what got scheduled, what got skipped, and why."""

    scheduled: list[Task] = field(default_factory=list)
    skipped: list[Task] = field(default_factory=list)
    total_minutes: int = 0

    def explain(self) -> str:
        """Return a human-readable explanation of the scheduling choices."""
        lines = [f"Daily plan ({self.total_minutes} min scheduled):"]
        for i, task in enumerate(self.scheduled, start=1):
            pet = task.pet.name if task.pet else "?"
            lines.append(
                f"  {i}. {task.due_time} — {task.title} for {pet} "
                f"({task.duration_minutes} min, {task.priority}) [scheduled]"
            )
        for task in self.skipped:
            pet = task.pet.name if task.pet else "?"
            lines.append(
                f"  -  {task.title} for {pet} "
                f"({task.duration_minutes} min, {task.priority}) "
                f"[skipped: not enough time in budget]"
            )
        return "\n".join(lines)

    def to_table(self) -> list:
        """Return plan rows suitable for display (e.g. in Streamlit)."""
        rows = []
        for task in self.scheduled:
            rows.append(self._row(task, "scheduled"))
        for task in self.skipped:
            rows.append(self._row(task, "skipped"))
        return rows

    @staticmethod
    def _row(task: Task, status: str) -> dict:
        """Build one display row dict for a task with the given status."""
        return {
            "pet": task.pet.name if task.pet else "?",
            "task": task.title,
            "due_time": task.due_time,
            "duration_minutes": task.duration_minutes,
            "priority": task.priority,
            "status": status,
        }


@dataclass
class Scheduler:
    """Builds a daily plan from tasks across all of an owner's pets."""

    pets: list[Pet]
    time_budget_minutes: int

    def all_tasks(self) -> list[Task]:
        """Gather every task across all pets into one flat list."""
        return [task for pet in self.pets for task in pet.tasks]

    def sort_by_priority(self) -> list[Task]:
        """Algorithmic feature #1: tasks sorted by priority (highest first).

        Ties are broken by due_time so the schedule reads in time order.
        """
        return sorted(
            self.all_tasks(),
            key=lambda t: (-t.priority_rank(), t.due_time),
        )

    def sort_by_time(self) -> list[Task]:
        """Return tasks across all pets sorted by due_time ("HH:MM")."""
        return sorted(self.all_tasks(), key=lambda t: t.due_time)

    def filter_pending(self) -> list[Task]:
        """Algorithmic feature #2: only tasks that are not yet completed."""
        return [task for task in self.all_tasks() if not task.completed]

    def filter_by_status(self, completed: bool) -> list[Task]:
        """Return tasks matching the given completion status."""
        return [task for task in self.all_tasks() if task.completed == completed]

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Return tasks belonging to the pet with the given name."""
        return [
            task
            for task in self.all_tasks()
            if task.pet is not None and task.pet.name == pet_name
        ]

    def detect_conflicts(self) -> list[str]:
        """Return warning strings for tasks that share the same due_time.

        Lightweight strategy: flags exact time matches only (not overlapping
        durations) and returns warnings instead of raising.
        """
        by_time: dict[str, list[Task]] = {}
        for task in self.all_tasks():
            by_time.setdefault(task.due_time, []).append(task)

        warnings = []
        for due_time, tasks in sorted(by_time.items()):
            if len(tasks) > 1:
                labels = ", ".join(
                    f"{t.title} ({t.pet.name if t.pet else '?'})" for t in tasks
                )
                warnings.append(f"⚠️ Conflict at {due_time}: {labels}")
        return warnings

    def build_plan(self) -> Plan:
        """Select and order tasks within the time budget; return a Plan.

        Greedy by priority: walk pending tasks highest-priority first and add
        each one that still fits the remaining budget; otherwise skip it.
        """
        candidates = [t for t in self.sort_by_priority() if not t.completed]
        scheduled: list[Task] = []
        skipped: list[Task] = []
        remaining = self.time_budget_minutes
        for task in candidates:
            if task.duration_minutes <= remaining:
                scheduled.append(task)
                remaining -= task.duration_minutes
            else:
                skipped.append(task)
        total = self.time_budget_minutes - remaining
        return Plan(scheduled=scheduled, skipped=skipped, total_minutes=total)
