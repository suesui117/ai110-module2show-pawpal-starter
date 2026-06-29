# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app that helps a pet owner plan daily care tasks across
all of their pets. Tasks live on each pet; a `Scheduler` gathers them across pets
and produces an explained daily plan that fits a time budget.

## ✨ Features

- **Multi-pet management** — one owner, many pets, each with its own care tasks (CRUD).
- **Sorting by priority** (`Scheduler.sort_by_priority()`) — highest-priority tasks first, ties broken by due time.
- **Sorting by time** (`Scheduler.sort_by_time()`) — chronological view of every task across pets.
- **Filtering** (`filter_pending()`, `filter_by_status()`, `filter_by_pet()`) — by completion status or pet.
- **Conflict warnings** (`Scheduler.detect_conflicts()`) — flags tasks booked at the same time.
- **Daily recurrence** (`Task.mark_complete()` → `Task.next_occurrence()`) — completing a `daily`/`weekly` task auto-schedules the next one.
- **Explained daily plan** (`Scheduler.build_plan()` → `Plan.explain()`) — greedy priority-fit within a time budget, with reasons for what was scheduled or skipped.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Running the demo script shows how PawPal+ builds a daily plan across multiple pets:

```bash
python main.py
```

```
PawPal+ — Today's Schedule for Sue
Pets: Mochi, Biscuit
Total tasks across all pets: 5
--------------------------------------------------
Daily plan (60 min scheduled):
  1. 08:00 — Morning feeding for Mochi (10 min, high) [scheduled]
  2. 08:30 — Morning walk for Biscuit (45 min, high) [scheduled]
  3. 09:00 — Medication for Biscuit (5 min, medium) [scheduled]
  -  Long hike for Biscuit (90 min, low) [skipped: not enough time in budget]
  -  Evening brushing for Mochi (15 min, low) [skipped: not enough time in budget]
```

The Scheduler gathers tasks from every pet, sorts them by priority (ties broken
by due time), and greedily fits them into the daily time budget — skipping
lower-priority tasks when time runs out.

## 🧪 Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

**What the tests cover** (`tests/test_pawpal.py`, 11 tests):

- **Core behavior** — `mark_complete()` flips status; `add_task` grows a pet's task list
- **Sorting correctness** — `sort_by_priority()` and `sort_by_time()` order tasks across multiple pets
- **Recurrence logic** — completing a `daily` task spawns the next occurrence; a `weekly` task advances 7 days
- **Conflict detection** — same-time tasks are flagged; differing times produce no false positives
- **Scheduling/edge cases** — `build_plan()` respects the time budget, an empty scheduler returns an empty plan, and a task larger than the whole budget is skipped (not deadlocked)

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.14.3, pytest-9.1.1, pluggy-1.6.0
collected 11 items

tests/test_pawpal.py ...........                                         [100%]

============================== 11 passed in 0.04s ==============================
```

**Confidence level: ★★★★☆ (4/5)** — all happy paths and the main edge cases
(empty schedules, oversized tasks, exact-time conflicts, recurrence) are covered
and passing. The remaining star is held back because conflict detection only
catches exact `due_time` matches, not overlapping durations, and recurrence has
no end date — both are documented tradeoffs rather than bugs.

## 📐 Smarter Scheduling

PawPal+ adds several algorithmic features on top of basic CRUD, all living in the
`Scheduler` (and `Task`) classes and working **across multiple pets**:

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_priority()`, `Scheduler.sort_by_time()` | Priority sort breaks ties by due time; time sort orders by `"HH:MM"` |
| Filtering | `Scheduler.filter_pending()`, `Scheduler.filter_by_status()`, `Scheduler.filter_by_pet()` | Filter by completion status or by pet name |
| Conflict handling | `Scheduler.detect_conflicts()` | Flags tasks sharing the exact same `due_time`; returns warning strings instead of raising |
| Recurring tasks | `Task.mark_complete()`, `Task.next_occurrence()` | Completing a `daily`/`weekly` task auto-spawns the next occurrence using `timedelta` |
| Daily plan | `Scheduler.build_plan()` → `Plan.explain()` | Greedy priority-fit within a time budget, with a human-readable explanation |

## 📸 Demo Walkthrough

### Main UI features (Streamlit, `app.py`)

- **Owner & pets** — set the owner name and add pets (name, species, breed, age).
- **Add tasks** — for any pet, enter a title, due time, duration, priority, and a
  *Repeats* option (`none` / `daily` / `weekly`).
- **Current pets & tasks** — each pet shows its task list in a table.
- **Build today's schedule** — pick a time budget and generate the plan. The app
  shows conflict warnings, the budgeted plan, a time-sorted view of all tasks, and
  an expandable "Why this plan?" explanation.

### Example workflow

1. Set the owner name (e.g. *Sue*).
2. Add a pet → **Mochi** (cat). Add a second pet → **Biscuit** (dog).
3. Add tasks: *Morning feeding* 08:00 for Mochi (daily), *Morning walk* 08:00 for
   Biscuit, *Medication* 09:00 for Biscuit, plus a couple of low-priority evening tasks.
4. Set the time budget to **60 minutes** and click **Generate schedule**.
5. View today's schedule — note the conflict warning, the priority-fit plan, and the
   time-sorted task list.

### Key Scheduler behaviors shown

- **Sorting** — tasks added out of order appear chronologically (`sort_by_time`) and
  by priority in the plan (`sort_by_priority`).
- **Conflict warnings** — two 08:00 tasks trigger a ⚠️ warning (`detect_conflicts`).
- **Budgeting** — the plan fits high-priority tasks first and skips what doesn't fit.
- **Recurrence** — completing the daily feeding schedules tomorrow's copy.

### Sample CLI output (`python main.py`)

```
PawPal+ — Today's Schedule for Sue
Pets: Mochi, Biscuit
=======================================================

[Sorted by time]
  08:00  Morning feeding (Mochi)
  08:00  Morning walk (Biscuit)
  09:00  Medication (Biscuit)
  17:00  Long hike (Biscuit)
  19:00  Evening brushing (Mochi)

[Filter by pet: Biscuit]
  17:00  Long hike
  08:00  Morning walk
  09:00  Medication

[Conflict detection]
  ⚠️ Conflict at 08:00: Morning feeding (Mochi), Morning walk (Biscuit)

[Recurring tasks]
  Completed 'Morning feeding' (daily) -> task count 5 to 6
  Next occurrence scheduled for: 2026-06-30

[Today's plan]
Daily plan (60 min scheduled):
  1. 08:00 — Morning feeding for Mochi (10 min, high) [scheduled]
  2. 08:00 — Morning walk for Biscuit (45 min, high) [scheduled]
  3. 09:00 — Medication for Biscuit (5 min, medium) [scheduled]
  -  Long hike for Biscuit (90 min, low) [skipped: not enough time in budget]
  -  Evening brushing for Mochi (15 min, low) [skipped: not enough time in budget]
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
