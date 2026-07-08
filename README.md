# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

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

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Today's Schedule
Today's plan:
  08:00 — Morning walk (30 min) [priority: high]
  09:00 — Feeding (10 min) [priority: high]
  18:00 — Brushing (15 min) [priority: low]
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```
collected 11 items                                                                                                                       
tests/test_pawpal.py ...........                                                                                                   [100%]

=========================================================== 11 passed in 0.03s ===========================================================

4 stars readability


## ✨ Features

- **Priority-based sorting** — orders tasks high → medium → low, breaking ties by earliest preferred time
- **Time-based sorting** — orders tasks earliest-to-latest by preferred time, with no-time tasks last
- **Time-budget filtering** — greedily fits as many tasks as possible into the owner's available minutes for the day
- **Task filtering** — filters tasks across all pets by completion status and/or pet name
- **Conflict warnings** — flags tasks (same pet or different pets) scheduled at the same preferred time, without altering the plan
- **Conflict resolution** — when building the final plan, drops lower-priority tasks that collide with an already-claimed time slot
- **Daily & weekly recurrence** — completion-triggered recurring tasks automatically generate their next due occurrence
- **Overdue/missed-task tracking** — due and overdue tasks keep appearing in the plan until completed, instead of silently disappearing
- **Plan explanation** — renders the generated plan as a human-readable, time-ordered summary

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_priority()`, `Scheduler.sort_by_time()` | Single composite-key sort (`priority_rank`, `preferred_time`) so "high" always comes before "medium"/"low"; same-priority tasks are then ordered earliest-time-first, with no-time tasks last. |
| Filtering | `Owner.filter_tasks()`, `Scheduler.filter_by_time()` | `Owner.filter_tasks()` filters across all pets by completion status and/or pet name (either or both, combined with AND). `Scheduler.filter_by_time()` greedily keeps only the tasks (in priority order) that still fit the owner's available time budget. |
| Conflict handling | `Scheduler.detect_time_conflicts()`, `Scheduler.resolve_conflicts()` | `detect_time_conflicts()` is a lightweight, non-destructive check: it groups tasks by exact `preferred_time` and returns human-readable warning strings for any slot shared by two or more tasks (same pet or different pets) — it never raises or drops anything. `resolve_conflicts()` is what actually shapes the final plan: once a time slot is claimed by a higher-priority task, later tasks requesting that same time are dropped. |
| Recurring tasks | `Task.build_next_occurrence()`, `Pet.mark_task_complete()`, `Task.is_due()` | Recurrence is completion-triggered, not calendar-driven: `Pet.mark_task_complete()` marks a task done and, if it's recurring, marks that instance `superseded` and appends a new `Task` from `Task.build_next_occurrence()`, whose `due_date` is computed with `timedelta` (`+1 day` for `"daily"`, `+7 days` for `"weekly"`). `Task.is_due()` then ensures only that one live instance of a recurring series appears in the plan at a time, while a missed (never-completed) occurrence keeps showing up as overdue instead of silently disappearing. |

## 📸 Demo Walkthrough

### UI features

The Streamlit app (`app.py`) is organized into four sections, each backed by the `pawpal_system` classes:

- **Owner** — enter the owner's name, which creates an `Owner` for the session.
- **Add a Pet** — enter a name, species, and breed, then click **Add pet** to attach a `Pet` to the owner. Added pets appear in a live table.
- **Add a Task** — pick a pet, then set a title, duration, priority, category, and preferred time, and click **Add task** to attach a `Task` to that pet. The current task table updates immediately, with:
  - A **conflict banner** (✅ success or ⚠️ warning per clashing time slot) from `Scheduler.detect_time_conflicts()`
  - A **sort toggle** (Priority / Time) that re-orders the table live via `Scheduler.sort_by_priority()` or `Scheduler.sort_by_time()`
- **Build Schedule** — enter the owner's available minutes for the day and click **Generate schedule** to run `Scheduler.generate_daily_plan()`. This re-checks for conflicts, then shows the resulting plan as a table with a success/info banner.

### Example workflow

1. Enter an owner name (e.g., "Jordan").
2. Add a pet (e.g., "Mochi", dog).
3. Add a task for that pet (e.g., "Morning walk", 30 min, high priority, 8:00 AM).
4. Add a second pet ("Rex") and a task that collides on time (e.g., "Litter box cleaning" also at 8:00 AM) — the task table immediately shows a ⚠️ conflict warning naming both pets and tasks.
5. Enter the available time for the day and click **Generate schedule** — the app re-checks conflicts, then displays the ordered plan that fits the time budget.

### Key Scheduler behaviors shown

- **Priority + time sorting** — high-priority tasks are placed first; ties are broken by earliest preferred time.
- **Time-budget filtering** — only as many tasks as fit the available minutes are kept, favoring earlier/higher-priority ones.
- **Conflict warnings** — tasks sharing a preferred time (even across different pets) are flagged with a human-readable warning instead of failing silently.
- **Conflict resolution** — when building the final plan, only the first task to claim a time slot survives; later colliding tasks are dropped.

### Sample CLI output

Running `python main.py` seeds an owner with two pets and a deliberate time collision, then prints the conflict warning followed by the generated plan:

```
Scheduling Conflicts
  Warning: conflict at 08:00 — Mochi's Morning walk, Rex's Litter box cleaning are all scheduled at the same time.

Today's Schedule
Today's plan:
  08:00 — Morning walk (30 min) [priority: high]
  09:00 — Feeding (10 min) [priority: high]
  18:00 — Brushing (15 min) [priority: low]
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
