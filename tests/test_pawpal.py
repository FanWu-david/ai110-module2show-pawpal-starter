from datetime import date, time, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


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

    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)


def test_completing_non_recurring_task_does_not_spawn_next_occurrence():
    pet = Pet(name="Mochi", species="dog", breed="Golden Retriever")
    task = Task(title="Vet visit", category="other", duration_minutes=60, priority="high")
    pet.add_task(task)

    next_task = pet.mark_task_complete(task.task_id)

    assert next_task is None
    assert len(pet.get_daily_tasks()) == 1


def test_recurring_task_successor_appears_in_next_days_plan():
    owner = Owner(name="Alex", contact_info="alex@example.com")
    pet = Pet(name="Mochi", species="dog", breed="Golden Retriever")
    owner.add_pet(pet)
    task = Task(
        title="Feeding", category="feeding", duration_minutes=10, priority="high",
        is_recurring=True, recurrence_pattern="daily",
    )
    pet.add_task(task)
    today = date(2026, 7, 7)
    tomorrow = today + timedelta(days=1)

    pet.mark_task_complete(task.task_id, for_date=today)
    scheduler = Scheduler(available_time_minutes=60)

    plan_today = scheduler.generate_daily_plan(owner, for_date=today)
    plan_tomorrow = scheduler.generate_daily_plan(owner, for_date=tomorrow)

    assert plan_today == []
    assert len(plan_tomorrow) == 1
    assert plan_tomorrow[0].due_date == tomorrow


def test_sort_by_time_returns_chronological_order():
    scheduler = Scheduler(available_time_minutes=180)
    morning = Task(
        title="Breakfast", category="feeding", duration_minutes=10, priority="low",
        preferred_time=time(8, 0),
    )
    midday = Task(
        title="Walk", category="walk", duration_minutes=20, priority="low",
        preferred_time=time(12, 0),
    )
    evening = Task(
        title="Dinner", category="feeding", duration_minutes=10, priority="low",
        preferred_time=time(18, 0),
    )
    no_time = Task(title="Brush", category="grooming", duration_minutes=5, priority="low")

    ordered = scheduler.sort_by_time([evening, no_time, morning, midday])

    assert [task.title for task in ordered] == ["Breakfast", "Walk", "Dinner", "Brush"]


def test_generate_daily_plan_is_chronological_within_same_priority():
    owner = Owner(name="Alex", contact_info="alex@example.com")
    pet = Pet(name="Mochi", species="dog", breed="Golden Retriever")
    owner.add_pet(pet)
    pet.add_task(Task(
        title="Dinner", category="feeding", duration_minutes=10, priority="medium",
        preferred_time=time(18, 0),
    ))
    pet.add_task(Task(
        title="Breakfast", category="feeding", duration_minutes=10, priority="medium",
        preferred_time=time(8, 0),
    ))
    pet.add_task(Task(
        title="Walk", category="walk", duration_minutes=10, priority="medium",
        preferred_time=time(12, 0),
    ))

    scheduler = Scheduler(available_time_minutes=60)
    plan = scheduler.generate_daily_plan(owner)

    assert [task.title for task in plan] == ["Breakfast", "Walk", "Dinner"]


def test_detect_time_conflicts_flags_duplicate_times_across_pets():
    owner = Owner(name="Alex", contact_info="alex@example.com")
    mochi = Pet(name="Mochi", species="dog", breed="Golden Retriever")
    rex = Pet(name="Rex", species="dog", breed="Lab")
    owner.add_pet(mochi)
    owner.add_pet(rex)
    mochi.add_task(Task(
        title="Walk", category="walk", duration_minutes=20, priority="high",
        preferred_time=time(9, 0),
    ))
    rex.add_task(Task(
        title="Feeding", category="feeding", duration_minutes=10, priority="high",
        preferred_time=time(9, 0),
    ))

    scheduler = Scheduler(available_time_minutes=120)
    warnings = scheduler.detect_time_conflicts(owner)

    assert len(warnings) == 1
    assert "09:00" in warnings[0]
    assert "Mochi" in warnings[0]
    assert "Rex" in warnings[0]


def test_detect_time_conflicts_returns_empty_when_no_overlap():
    owner = Owner(name="Alex", contact_info="alex@example.com")
    pet = Pet(name="Mochi", species="dog", breed="Golden Retriever")
    owner.add_pet(pet)
    pet.add_task(Task(
        title="Walk", category="walk", duration_minutes=20, priority="high",
        preferred_time=time(9, 0),
    ))
    pet.add_task(Task(
        title="Feeding", category="feeding", duration_minutes=10, priority="high",
        preferred_time=time(10, 0),
    ))

    scheduler = Scheduler(available_time_minutes=120)

    assert scheduler.detect_time_conflicts(owner) == []


def test_generate_daily_plan_drops_second_task_on_time_collision():
    owner = Owner(name="Alex", contact_info="alex@example.com")
    mochi = Pet(name="Mochi", species="dog", breed="Golden Retriever")
    rex = Pet(name="Rex", species="dog", breed="Lab")
    owner.add_pet(mochi)
    owner.add_pet(rex)
    mochi.add_task(Task(
        title="Walk", category="walk", duration_minutes=20, priority="high",
        preferred_time=time(9, 0),
    ))
    rex.add_task(Task(
        title="Feeding", category="feeding", duration_minutes=10, priority="low",
        preferred_time=time(9, 0),
    ))

    scheduler = Scheduler(available_time_minutes=120)
    plan = scheduler.generate_daily_plan(owner)

    assert [task.title for task in plan] == ["Walk"]
