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

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff is in `detect_conflicts()`: it only flags tasks that share the **exact same `due_time`**, not tasks whose **durations overlap** (e.g. an 08:00 task lasting 45 min running into an 08:30 task). I chose exact-match because it keeps the logic simple and predictable — it compares time strings directly, returns plain warning messages instead of raising, and is easy to test. True overlap detection would require parsing every `due_time` into minutes, adding `duration_minutes`, and comparing intervals pairwise, which is more code and more edge cases than this assignment needs. For a pet owner glancing at a daily plan, "two things booked at 08:00" is the most common and most useful conflict to catch, so the simpler version covers the realistic case while staying readable.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
