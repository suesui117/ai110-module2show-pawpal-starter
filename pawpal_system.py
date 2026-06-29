"""PawPal+ logic layer.

Class skeletons generated from diagrams/uml.mmd. Data-holding objects use
dataclasses to stay clean. Behavior methods are empty stubs to implement
incrementally.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
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
        ...

    def priority_rank(self) -> int:
        """Return a sortable number for this task's priority (higher = more urgent)."""
        ...


@dataclass
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
        ...

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        ...

    def list_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        ...


@dataclass
class Owner:
    """A pet owner. Holds identity and the pets they own."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner and link the pet back to this owner."""
        ...

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        ...


@dataclass
class Plan:
    """The result of scheduling: what got scheduled, what got skipped, and why."""

    scheduled: list[Task] = field(default_factory=list)
    skipped: list[Task] = field(default_factory=list)
    total_minutes: int = 0

    def explain(self) -> str:
        """Return a human-readable explanation of the scheduling choices."""
        ...

    def to_table(self) -> list:
        """Return plan rows suitable for display (e.g. in Streamlit)."""
        ...


@dataclass
class Scheduler:
    """Builds a daily plan from tasks across all of an owner's pets."""

    pets: list[Pet]
    time_budget_minutes: int

    def all_tasks(self) -> list[Task]:
        """Gather every task across all pets into one flat list."""
        ...

    def sort_by_priority(self) -> list[Task]:
        """Algorithmic feature #1: tasks sorted by priority (highest first)."""
        ...

    def filter_pending(self) -> list[Task]:
        """Algorithmic feature #2: only tasks that are not yet completed."""
        ...

    def build_plan(self) -> Plan:
        """Select and order tasks within the time budget; return a Plan."""
        ...
