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
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_priority()`, `Scheduler.sort_by_time()` | Single composite-key sort (`priority_rank`, `preferred_time`) so "high" always comes before "medium"/"low"; same-priority tasks are then ordered earliest-time-first, with no-time tasks last. |
| Filtering | `Owner.filter_tasks()`, `Scheduler.filter_by_time()` | `Owner.filter_tasks()` filters across all pets by completion status and/or pet name (either or both, combined with AND). `Scheduler.filter_by_time()` greedily keeps only the tasks (in priority order) that still fit the owner's available time budget. |
| Conflict handling | `Scheduler.detect_time_conflicts()`, `Scheduler.resolve_conflicts()` | `detect_time_conflicts()` is a lightweight, non-destructive check: it groups tasks by exact `preferred_time` and returns human-readable warning strings for any slot shared by two or more tasks (same pet or different pets) — it never raises or drops anything. `resolve_conflicts()` is what actually shapes the final plan: once a time slot is claimed by a higher-priority task, later tasks requesting that same time are dropped. |
| Recurring tasks | `Task.build_next_occurrence()`, `Pet.mark_task_complete()`, `Task.is_due()` | Recurrence is completion-triggered, not calendar-driven: `Pet.mark_task_complete()` marks a task done and, if it's recurring, marks that instance `superseded` and appends a new `Task` from `Task.build_next_occurrence()`, whose `due_date` is computed with `timedelta` (`+1 day` for `"daily"`, `+7 days` for `"weekly"`). `Task.is_due()` then ensures only that one live instance of a recurring series appears in the plan at a time, while a missed (never-completed) occurrence keeps showing up as overdue instead of silently disappearing. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
