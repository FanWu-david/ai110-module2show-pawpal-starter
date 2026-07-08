# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
    <3 core actions a user can do>:
        1. Add a pet (type, species, name..)
        2. schedule a task (e.g. walking, feeding, )
        3. see today's task (e.g. notification, checklist)

- What classes did you include, and what responsibilities did you assign to each?
Four required classes: Owner, Pet, Task, Scheduler
Brainstorm: probably some type of a customized object for pet, 
        with attributes of type, species, name, 
        and a vector or some type of list for holding and accessing daily tasks
     - methods for viewing these attributes
     - methods for changing these attributes, with some type of access control for users
     - methods for displaying the daily task
     - methods for adding, removing or modifying task into the list of daily task
     
- The classes I chose to include were Owner, Pet, Task, and Scheduler. 
    - Owner contains information for the user, methods for accessing the info, and a list of pets
    - Pet contains information for the pet, methods for accessing the info, and a list of tasks 
    - Task contains information for the task, methods for accessing the info
    - Scheduler contains methods that can read users' preference, read daily tasks of pets and arrange order for tasks.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

While generating the Python skeleton from the UML, review surfaced the following gaps to address before implementing logic:

Missing relationships:
- [FIXED] No back-reference from Task -> Pet (or Pet -> Owner). A Task on its own couldn't identify which pet it belongs to, which limited any cross-pet view. Fixed by adding Task.pet_id (defaults to None) and having Pet.add_task() stamp task.pet_id = self.pet_id when the task is added.
- [FIXED] No ID generation strategy for task_id / pet_id / owner_id — were required fields with no default, so nothing guaranteed uniqueness. Fixed by making each ID auto-generate via uuid4 (default_factory on the Task/Pet dataclasses, `owner_id or str(uuid4())` in Owner.__init__) when the caller doesn't supply one, and reordering the dataclass fields so the defaulted ID field comes after the required fields.
- [FIXED] Two sources of truth for constraints: Scheduler stores its own available_time_minutes / constraints from __init__, but generate_daily_plan also receives owner (whose preferences presumably encode constraints too). Fixed by adding Scheduler.resolve_constraints(owner), which starts from the Scheduler's own defaults and then overlays owner.get_preferences() on top — so on any conflicting key, the owner's preference wins. generate_daily_plan should call this instead of reading self.available_time_minutes / self.constraints directly once its logic is implemented.

Logic bottlenecks:
- [FIXED] Multi-pet scheduling isn't handled: Owner could have 0..* pets, but generate_daily_plan(pet, owner) only accepted one pet and available_time_minutes was a single fixed budget, so calling it once per pet would have double-booked the owner's actual day. Fixed by adding Owner.get_all_tasks() (flattens daily_tasks across every pet) and changing generate_daily_plan's signature to generate_daily_plan(owner, for_date=None) — it now pulls candidate tasks across all of the owner's pets and schedules them against one shared, resolved time budget.
- [FIXED, as a side effect] Duplicate time parameter: filter_by_time(tasks, available_time) still takes available_time as an explicit argument (kept so the method stays pure/testable in isolation), but generate_daily_plan now always computes it once via resolve_constraints(owner) and threads that single value through — so there's one authoritative value per scheduling run instead of two that could drift.
- [FIXED] Undefined pipeline order inside generate_daily_plan: now explicitly filter out already-completed tasks for the date -> sort_by_priority -> filter_by_time (greedy, priority order, within budget) -> resolve_conflicts (drops tasks whose preferred_time collides with an already-selected task). Verified with a manual smoke test (two pets, an 8:00 walk and an 8:00 feeding task): the owner's preferences overrode the Scheduler's default time budget, tasks were pooled across both pets, and the conflicting same-time task was correctly dropped.
- [FIXED] Recurring + completed conflict: is_recurring/recurrence_pattern and completed/mark_complete() coexisted on the same Task, but nothing reset completed for the next occurrence — marking a daily recurring task done once would have removed it from every future plan. Fixed by replacing the single completed: bool with completed_dates: set[date] on Task. mark_complete(for_date=None) adds a date (defaulting to today) instead of flipping one flag, and is_complete(for_date=None) checks whether that specific date is in the set. A recurring task and a one-off task now use the same mechanism — a one-off task just ends up with a set containing at most one date. This avoids introducing a 5th class (e.g. separate "template" vs "instance" objects), which would have broken the assignment's 4-required-classes constraint.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

Greedy, priority-ordered time-boxing instead of optimal packing. filter_by_time (pawpal_system.py:268-276) fills the available time budget by walking tasks in priority order and taking each one that still fits — it never looks ahead to ask "would dropping this high-priority task let two lower-priority ones fit instead, using the time more fully?" That's a classic knapsack problem, and solving it optimally would trade simplicity for a much more complex algorithm.

This tradeoff is reasonable here because for a pet owner, which tasks get done (medication and feeding before optional grooming) matters more than squeezing every last minute out of the schedule — dropping a high-priority task to fit two low-priority ones would be actively bad, not just suboptimal.
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
