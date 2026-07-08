from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from uuid import uuid4

EDITABLE_TASK_FIELDS = {
    "title", "category", "duration_minutes", "priority",
    "preferred_time", "is_recurring", "recurrence_pattern",
}

RECURRENCE_INTERVALS = {
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
}


@dataclass
class Task:
    title: str
    category: str
    duration_minutes: int
    priority: str
    task_id: str = field(default_factory=lambda: str(uuid4()))
    pet_id: str | None = None
    preferred_time: time | None = None
    is_recurring: bool = False
    recurrence_pattern: str | None = None
    completed_dates: set[date] = field(default_factory=set)
    due_date: date | None = None
    superseded: bool = False

    def get_details(self) -> dict:
        """Return this task's fields as a dict."""
        return {
            "task_id": self.task_id,
            "pet_id": self.pet_id,
            "title": self.title,
            "category": self.category,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "preferred_time": self.preferred_time,
            "is_recurring": self.is_recurring,
            "recurrence_pattern": self.recurrence_pattern,
            "due_date": self.due_date,
        }

    def update_details(self, updates: dict) -> None:
        """Apply a partial update to this task's editable fields."""
        unknown = set(updates) - EDITABLE_TASK_FIELDS
        if unknown:
            raise ValueError(f"Cannot update unknown or protected field(s): {sorted(unknown)}")
        for key, value in updates.items():
            setattr(self, key, value)

    def mark_complete(self, for_date: date | None = None) -> None:
        """Record this task as completed for the given date (default today)."""
        self.completed_dates.add(for_date or date.today())

    def is_complete(self, for_date: date | None = None) -> bool:
        """Check whether this task was completed on the given date (default today)."""
        return (for_date or date.today()) in self.completed_dates

    def is_due(self, for_date: date | None = None) -> bool:
        """Check whether this task's due date has arrived and it hasn't been replaced by a successor.

        Tasks with no due date are always due. A missed occurrence (due date passed,
        never completed) keeps showing up rather than silently disappearing.

        Args:
            for_date: The date to check against (defaults to today).

        Returns:
            False if this task has been superseded by a spawned successor, or if
            its due date hasn't arrived yet; True otherwise.
        """
        if self.superseded:
            return False
        return self.due_date is None or self.due_date <= (for_date or date.today())

    def build_next_occurrence(self, completed_on: date | None = None) -> "Task | None":
        """If this task recurs, return a new Task instance due on its next occurrence.

        Uses timedelta so "daily" lands exactly one day after completion and
        "weekly" exactly seven, regardless of month/year boundaries.

        Args:
            completed_on: The date this occurrence was completed (defaults to
                today); the next occurrence's due_date is computed relative to it.

        Returns:
            A new Task carrying the same details with due_date advanced by the
            recurrence interval, or None if this task isn't recurring (or its
            recurrence_pattern isn't one of RECURRENCE_INTERVALS).
        """
        if not self.is_recurring or self.recurrence_pattern is None:
            return None
        interval = RECURRENCE_INTERVALS.get(self.recurrence_pattern.lower())
        if interval is None:
            return None
        next_due = (completed_on or date.today()) + interval
        return Task(
            title=self.title,
            category=self.category,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            pet_id=self.pet_id,
            preferred_time=self.preferred_time,
            is_recurring=self.is_recurring,
            recurrence_pattern=self.recurrence_pattern,
            due_date=next_due,
        )

    def is_overdue(self, now: datetime | None = None) -> bool:
        """Check whether this task's preferred time has passed today without completion."""
        if self.preferred_time is None:
            return False
        now = now or datetime.now()
        if self.is_complete(now.date()):
            return False
        return now.time() > self.preferred_time


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    pet_id: str = field(default_factory=lambda: str(uuid4()))
    daily_tasks: list[Task] = field(default_factory=list)

    def get_info(self) -> dict:
        """Return this pet's basic info as a dict."""
        return {"pet_id": self.pet_id, "name": self.name, "species": self.species, "breed": self.breed}

    def update_info(self, name: str, species: str, breed: str) -> None:
        """Update this pet's name, species, and breed."""
        self.name = name
        self.species = species
        self.breed = breed

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet, stamping it with this pet's ID."""
        task.pet_id = self.pet_id
        self.daily_tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove the task with the given ID from this pet's task list."""
        self.daily_tasks = [task for task in self.daily_tasks if task.task_id != task_id]

    def modify_task(self, task_id: str, updates: dict) -> None:
        """Apply a partial update to the task with the given ID."""
        for task in self.daily_tasks:
            if task.task_id == task_id:
                task.update_details(updates)
                return
        raise ValueError(f"No task found with task_id: {task_id}")

    def mark_task_complete(self, task_id: str, for_date: date | None = None) -> Task | None:
        """Mark a task complete and, if it recurs, schedule its next occurrence.

        Scans this pet's tasks for a matching ID (O(n)), marks it complete, and if
        it's recurring, marks it superseded and appends its freshly built successor.

        Args:
            task_id: The ID of the task to complete.
            for_date: The date to record completion for (defaults to today).

        Returns:
            The newly created next-occurrence Task, or None if the task doesn't recur.

        Raises:
            ValueError: If no task with task_id exists on this pet.
        """
        for task in self.daily_tasks:
            if task.task_id == task_id:
                task.mark_complete(for_date)
                next_task = task.build_next_occurrence(for_date)
                if next_task is not None:
                    task.superseded = True
                    self.add_task(next_task)
                return next_task
        raise ValueError(f"No task found with task_id: {task_id}")

    def get_daily_tasks(self) -> list[Task]:
        """Return a copy of this pet's task list."""
        return list(self.daily_tasks)

    def display_daily_tasks(self) -> None:
        """Print this pet's tasks with their completion status."""
        if not self.daily_tasks:
            print(f"{self.name} has no tasks scheduled.")
            return
        print(f"Tasks for {self.name}:")
        for task in self.daily_tasks:
            status = "done" if task.is_complete() else "pending"
            print(
                f"  - [{status}] {task.title} ({task.category}, "
                f"{task.duration_minutes} min, priority: {task.priority})"
            )


class Owner:
    def __init__(self, name: str, contact_info: str, preferences: dict | None = None, owner_id: str | None = None):
        self.owner_id = owner_id or str(uuid4())
        self.name = name
        self.contact_info = contact_info
        self.preferences = preferences or {}
        self.pets: list[Pet] = []

    def get_name(self) -> str:
        """Return this owner's name."""
        return self.name

    def get_preferences(self) -> dict:
        """Return this owner's scheduling preferences."""
        return self.preferences

    def update_preferences(self, prefs: dict) -> None:
        """Merge new values into this owner's preferences."""
        self.preferences.update(prefs)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        """Remove the pet with the given ID from this owner's list of pets."""
        self.pets = [pet for pet in self.pets if pet.pet_id != pet_id]

    def get_pets(self) -> list[Pet]:
        """Return a copy of this owner's list of pets."""
        return list(self.pets)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.get_daily_tasks()]

    def filter_tasks(
        self,
        completed: bool | None = None,
        pet_name: str | None = None,
        for_date: date | None = None,
    ) -> list[Task]:
        """Return tasks across all pets, optionally filtered by completion status and/or pet name.

        Args:
            completed: If set, keep only tasks whose completion status for
                for_date matches this value. If None, completion is ignored.
            pet_name: If set, keep only tasks belonging to pets with this exact name.
            for_date: The date to check completion against when `completed` is
                set (defaults to today).

        Returns:
            The filtered list of tasks; active filters are combined with AND.
        """
        tasks = self.get_all_tasks()
        if pet_name is not None:
            pet_ids = {pet.pet_id for pet in self.pets if pet.name == pet_name}
            tasks = [task for task in tasks if task.pet_id in pet_ids]
        if completed is not None:
            tasks = [task for task in tasks if task.is_complete(for_date) == completed]
        return tasks


class Scheduler:
    def __init__(self, available_time_minutes: int, constraints: dict | None = None):
        self.available_time_minutes = available_time_minutes
        self.constraints = constraints or {}

    def resolve_constraints(self, owner: Owner) -> dict:
        """Merge the scheduler's defaults with the owner's preferences, owner wins on conflicts."""
        resolved = {"available_time_minutes": self.available_time_minutes, **self.constraints}
        resolved.update(owner.get_preferences())
        return resolved

    def generate_daily_plan(self, owner: Owner, for_date: date | None = None) -> list[Task]:
        """Build a conflict-free, time-boxed plan across all of the owner's pets.

        Pipeline: gather due & incomplete tasks -> sort by priority (ties broken
        by time) -> greedily fit as many as possible within the time budget ->
        drop any that still collide on preferred time.

        Args:
            owner: The owner whose pets' tasks should be scheduled.
            for_date: The date to build the plan for (defaults to today).

        Returns:
            The ordered list of tasks selected for the plan.
        """
        for_date = for_date or date.today()
        available_time = self.resolve_constraints(owner).get(
            "available_time_minutes", self.available_time_minutes
        )
        candidates = [
            task for task in owner.get_all_tasks()
            if task.is_due(for_date) and not task.is_complete(for_date)
        ]
        ordered = self.sort_by_priority(candidates)
        within_budget = self.filter_by_time(ordered, available_time)
        return self.resolve_conflicts(within_budget)

    @staticmethod
    def _time_sort_key(task: Task) -> time:
        """Sort key for preferred_time; tasks with no preferred time sort last.

        Args:
            task: The task to compute a key for.

        Returns:
            task.preferred_time, or time.max (23:59:59.999999) if it's unset.
        """
        return task.preferred_time or time.max

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks from highest to lowest priority, breaking ties by preferred time.

        Single O(n log n) sort on a composite (priority_rank, time) key, so ties
        don't depend on Python's sort stability or a separate pre-sort pass.

        Args:
            tasks: The tasks to sort.

        Returns:
            A new list ordered "high" -> "medium" -> "low"; same-priority tasks
            are ordered earliest-time-first (no-time tasks last).
        """
        priority_rank = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            tasks,
            key=lambda task: (priority_rank.get(task.priority, len(priority_rank)), self._time_sort_key(task)),
        )

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by preferred time, tasks with no preferred time last.

        Args:
            tasks: The tasks to sort.

        Returns:
            A new list ordered earliest-time-first, with no-time tasks last.
        """
        return sorted(tasks, key=self._time_sort_key)

    def filter_by_time(self, tasks: list[Task], available_time: int) -> list[Task]:
        """Greedily select tasks, in order, that fit within the available time.

        Single pass, O(n): walks tasks in the given order, keeping each one
        whose duration still fits the remaining budget and skipping (not
        stopping at) any that don't, so later, shorter tasks still get a chance.
        This favors earlier/higher-priority tasks over maximizing total time
        used — see generate_daily_plan.

        Args:
            tasks: The candidate tasks, already in priority/selection order.
            available_time: The total time budget, in minutes.

        Returns:
            The subset of tasks that fit, in the same relative order.
        """
        selected: list[Task] = []
        remaining_time = available_time
        for task in tasks:
            if task.duration_minutes <= remaining_time:
                selected.append(task)
                remaining_time -= task.duration_minutes
        return selected

    def resolve_conflicts(self, tasks: list[Task]) -> list[Task]:
        """Drop tasks whose preferred time collides with an already-selected task.

        Single pass, O(n), using a set to track claimed time slots: once a
        preferred_time is claimed, any later task requesting that exact same
        time is dropped.

        Args:
            tasks: The candidate tasks, in the order priority/budget selected them.

        Returns:
            The subset of tasks where no two share the same preferred_time.
        """
        resolved: list[Task] = []
        claimed_times: set[time] = set()
        for task in tasks:
            if task.preferred_time is not None:
                if task.preferred_time in claimed_times:
                    continue
                claimed_times.add(task.preferred_time)
            resolved.append(task)
        return resolved

    def detect_time_conflicts(self, owner: Owner, for_date: date | None = None) -> list[str]:
        """Flag tasks (same pet or different pets) sharing a preferred time.

        Lightweight by design: groups today's due, incomplete tasks by exact
        preferred_time (O(n)) and reports any slot claimed by more than one
        task, rather than checking full duration-interval overlap. Never
        raises, so callers can log/display the warnings without the app crashing.

        Args:
            owner: The owner whose pets' tasks should be checked.
            for_date: The date to check (defaults to today).

        Returns:
            A human-readable warning string per conflicting time slot, or an
            empty list if there are no conflicts.
        """
        for_date = for_date or date.today()
        pet_names = {pet.pet_id: pet.name for pet in owner.get_pets()}
        tasks = [
            task for task in owner.get_all_tasks()
            if task.is_due(for_date) and not task.is_complete(for_date)
        ]

        by_time: dict[time, list[Task]] = {}
        for task in tasks:
            if task.preferred_time is not None:
                by_time.setdefault(task.preferred_time, []).append(task)

        warnings: list[str] = []
        for slot in sorted(by_time):
            clashing = by_time[slot]
            if len(clashing) > 1:
                labels = ", ".join(
                    f"{pet_names.get(task.pet_id, 'Unknown pet') if task.pet_id is not None else 'Unknown pet'}'s {task.title}"
                    for task in clashing
                )
                warnings.append(f"Warning: conflict at {slot.strftime('%H:%M')} — {labels} are all scheduled at the same time.")
        return warnings

    def explain_plan(self, plan: list[Task]) -> str:
        """Render a plan as a human-readable, time-ordered summary."""
        if not plan:
            return "No tasks fit into today's plan."
        lines = ["Today's plan:"]
        for task in plan:
            time_label = task.preferred_time.strftime("%H:%M") if task.preferred_time else "anytime"
            lines.append(f"  {time_label} — {task.title} ({task.duration_minutes} min) [priority: {task.priority}]")
        return "\n".join(lines)
