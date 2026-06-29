# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

1. Manage pets (CRUD). The user can create, view, edit, and delete pets. Each pet stores basic information such as name, species, breed, and age.
2. Manage care tasks (CRUD). The user can create, edit, and delete care tasks (such as feeding, walking, medication, and grooming) and assign each to a specific pet, with a duration and priority.
3. Generate a daily plan. Given the day's tasks and a time budget, the system selects and orders tasks by priority and constraints, and explains its choices (why each task was scheduled or skipped) as part of the output.

- What classes did you include, and what responsibilities did you assign to each?

I included five classes, organized around a single responsibility each (Owner → Pet → Task data hierarchy, plus a Scheduler that processes tasks and a Plan that holds the result):

- **Owner** — holds owner identity (name) and a list of pets; methods to add/remove pets.
- **Pet** — holds identifying info (name, species, breed, age), a back-reference to its owner, and its own list of tasks; methods to add/remove/list tasks.
- **Task** — represents one care activity: title, due time, duration, priority, completion status, and the pet it belongs to; `mark_complete()` and `priority_rank()` (maps priority to a sortable number).
- **Scheduler** — the "brain." Takes the owner's pets and a time budget, gathers tasks across all pets (`all_tasks()`), and applies algorithmic features (`sort_by_priority()`, `filter_pending()`) to build a daily plan.
- **Plan** — the scheduler's result: the scheduled tasks, the skipped tasks, total minutes used, and an `explain()` method describing why each task was scheduled or skipped.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes. After AI reviewed my class skeleton, I made two changes:

1. **Centralized the two-way links.** Owner↔Pet and Pet↔Task are bidirectional. I moved all the linking into `add_pet`/`add_task` so both sides are always set together (e.g. `add_task` sets `task.pet` *and* appends to `pet.tasks`). This prevents the two references from drifting out of sync.
2. **Switched the data classes to `@dataclass(eq=False)`.** By default a dataclass compares by field values, so two different tasks with identical fields would count as "equal" — meaning `list.remove()` could delete the wrong one. Using `eq=False` restores identity-based comparison, and I also made `remove_task`/`remove_pet` remove by identity (`is`) to be safe.

I verified both changes with a quick smoke test (add a pet/task, confirm both links resolve, mark complete, remove by identity).

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

My scheduler considers three constraints: a daily **time budget** (total minutes available), each task's **priority** (high/medium/low), and **completion status** (completed tasks are filtered out before planning). I decided time and priority mattered most because the scenario is a *busy* owner who can't do everything — so the real question is "what should I do first when I run out of time?" `build_plan()` answers that by sorting pending tasks highest-priority first (ties broken by due time) and greedily fitting them into the budget, skipping what doesn't fit. Owner preferences are a possible future constraint, but I left them out to keep the core logic focused on the two constraints that drive the daily decision.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff is in `detect_conflicts()`: it only flags tasks that share the **exact same `due_time`**, not tasks whose **durations overlap** (e.g. an 08:00 task lasting 45 min running into an 08:30 task). I chose exact-match because it keeps the logic simple and predictable — it compares time strings directly, returns plain warning messages instead of raising, and is easy to test. True overlap detection would require parsing every `due_time` into minutes, adding `duration_minutes`, and comparing intervals pairwise, which is more code and more edge cases than this assignment needs. For a pet owner glancing at a daily plan, "two things booked at 08:00" is the most common and most useful conflict to catch, so the simpler version covers the realistic case while staying readable.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used my AI coding assistant across every phase: brainstorming the core actions and class list, converting the UML into dataclass skeletons, implementing the scheduler logic, writing tests, and debugging. The most effective features were **agent/edit mode** (making coordinated edits across `pawpal_system.py`, `main.py`, tests, and the README at once) and **chat for conceptual questions**. The most helpful prompts were the focused, checkable ones — for example asking it to **cross-check my UML against the grading rubric line by line**, which caught that my `Task` class was missing `due_time`, `completed`, and `mark_complete()`. Concept questions like "is Pet-has-Task the right relationship?" and "how should the Scheduler get tasks from the Owner's pets?" were also useful because the answers shaped the design, not just the code.

**AI strategy notes:**

- **Most effective features:** rubric-aware code review, multi-file editing in agent mode, and quick CLI smoke tests to verify behavior before moving on.
- **Separate chat sessions per phase** kept design discussion from bleeding into testing details — when I started a fresh session for testing, the assistant focused only on edge cases (empty schedule, oversized task, same-time conflicts) instead of re-litigating design.
- **Being the "lead architect":** I treated AI suggestions as proposals to evaluate, not answers to paste. I kept the system simple on purpose (e.g. declining extra inheritance and exact-match conflict detection) and made the final calls on structure.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

Early on, the assistant proposed making **"Explain the plan" a third standalone core action**. I pushed back — an explanation isn't something a user triggers on its own, it's an *output* of generating the plan. So instead of a separate action, I folded the reasoning into `Plan.explain()`. I also questioned an inheritance idea (Pet/Task) and kept it as a simple `has-a` relationship. I verified AI suggestions in three ways: checking them against the **grading rubric**, running the **CLI demo** (`python main.py`) to see real behavior, and running the **pytest suite** (11 tests) to confirm sorting, recurrence, conflicts, and budgeting all behaved correctly. One concrete catch from the demo: a recurring-task test in `main.py` threw an `IndexError` because my selector grabbed the wrong task — running it surfaced the bug immediately, and the fix was in my demo code, not the scheduler logic.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I wrote 11 pytest tests covering: task completion (`mark_complete` flips status), task addition (a pet's task count grows), sorting correctness (`sort_by_priority` and `sort_by_time` across multiple pets), recurrence (completing a daily task spawns the next day's copy; weekly advances 7 days), conflict detection (same-time tasks flagged; differing times produce no false positives), and scheduling edge cases (budget respected, empty scheduler returns an empty plan, a task larger than the whole budget is skipped). These were important because sorting, recurrence, and conflict detection are the "smart" parts of the app — the places where a bug would silently produce a wrong plan rather than crash.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'm about **4 out of 5** confident. All happy paths and the main edge cases pass, and the logic is small enough to reason about. The reason it isn't 5/5 is that two known limitations are untested-by-design: conflict detection only catches **exact** time matches (not overlapping durations), and recurring tasks have **no end date**. With more time I'd test overlapping-duration conflicts, malformed `due_time` strings (e.g. `"9:00"` vs `"09:00"`), and a recurrence that should stop after a number of occurrences.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with the `Scheduler` "brain" working cleanly across multiple pets. It gathers every pet's tasks, sorts them by priority, fits them into a time budget, and — through `Plan.explain()` — tells the owner *why* each task was scheduled or skipped. The clear Owner → Pet → Task hierarchy made that logic simple to write and test.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I'd upgrade conflict detection to handle **overlapping durations**, not just exact start times, and give recurring tasks an **end condition** so they don't repeat forever. On the UI side, I'd add a way to mark tasks complete directly in Streamlit (which would make the recurrence feature visible in the browser) and persist data beyond a single session.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The biggest thing I learned is that my job as the human is **design judgment**, not typing speed. AI could generate classes, tests, and refactors quickly, but it was my decisions — keeping the model simple, rejecting an unnecessary "Explain" action and extra inheritance, choosing exact-match conflict detection on purpose — that kept the system coherent. Cross-checking AI output against the rubric and running the code to verify it mattered far more than accepting suggestions as-is.
