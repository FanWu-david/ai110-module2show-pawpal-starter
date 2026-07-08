from datetime import date, timedelta

from pawpal_system import Pet, Task


def test_mark_complete_changes_task_status():
    task = Task(title="Morning walk", category="walk", duration_minutes=30, priority="high")

    assert not task.is_complete()

    task.mark_complete()

    assert task.is_complete()


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog", breed="Golden Retriever")

    assert len(pet.get_daily_tasks()) == 0

    pet.add_task(Task(title="Feeding", category="feeding", duration_minutes=10, priority="high"))

    assert len(pet.get_daily_tasks()) == 1


def test_completing_daily_task_spawns_next_occurrence_one_day_later():
    pet = Pet(name="Mochi", species="dog", breed="Golden Retriever")
    task = Task(
        title="Feeding", category="feeding", duration_minutes=10, priority="high",
        is_recurring=True, recurrence_pattern="daily",
    )
    pet.add_task(task)
    today = date(2026, 7, 7)

    next_task = pet.mark_task_complete(task.task_id, for_date=today)

    assert task.is_complete(today)
    assert len(pet.get_daily_tasks()) == 2
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.task_id != task.task_id
    assert not next_task.is_complete(next_task.due_date)


def test_completing_weekly_task_spawns_next_occurrence_seven_days_later():
    pet = Pet(name="Rex", species="dog", breed="Lab")
    task = Task(
        title="Grooming", category="grooming", duration_minutes=45, priority="medium",
        is_recurring=True, recurrence_pattern="weekly",
    )
    pet.add_task(task)
    today = date(2026, 7, 7)

    next_task = pet.mark_task_complete(task.task_id, for_date=today)

    assert next_task.due_date == today + timedelta(weeks=1)


def test_completing_non_recurring_task_does_not_spawn_next_occurrence():
    pet = Pet(name="Mochi", species="dog", breed="Golden Retriever")
    task = Task(title="Vet visit", category="other", duration_minutes=60, priority="high")
    pet.add_task(task)

    next_task = pet.mark_task_complete(task.task_id)

    assert next_task is None
    assert len(pet.get_daily_tasks()) == 1
