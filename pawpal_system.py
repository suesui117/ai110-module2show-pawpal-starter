"""PawPal+ logic layer.

Class skeletons generated from diagrams/uml.mmd. Data-holding objects use
dataclasses to stay clean. Behavior methods are empty stubs to implement
incrementally.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(eq=False)
class Task:
    """A single care activity for one pet."""

    title: str
    due_time: str                 # e.g. "08:00"
    duration_minutes: int
    priority: str                 # "low" | "medium" | "high"
    completed: bool = False
    pet: "Pet | None" = None

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def priority_rank(self) -> int:
        """Return a sortable number for this task's priority (higher = more urgent)."""
        ranks = {"high": 3, "medium": 2, "low": 1}
        return ranks.get(self.priority.lower(), 0)


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

    def filter_pending(self) -> list[Task]:
        """Algorithmic feature #2: only tasks that are not yet completed."""
        return [task for task in self.all_tasks() if not task.completed]

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
