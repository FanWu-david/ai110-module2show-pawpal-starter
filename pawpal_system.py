from dataclasses import dataclass, field
from datetime import time


@dataclass
class Task:
    task_id: str
    title: str
    category: str
    duration_minutes: int
    priority: str
    preferred_time: time | None = None
    is_recurring: bool = False
    recurrence_pattern: str | None = None
    completed: bool = False

    def get_details(self) -> dict:
        raise NotImplementedError

    def update_details(self, updates: dict) -> None:
        raise NotImplementedError

    def mark_complete(self) -> None:
        raise NotImplementedError

    def is_overdue(self) -> bool:
        raise NotImplementedError


@dataclass
class Pet:
    pet_id: str
    name: str
    species: str
    breed: str
    daily_tasks: list[Task] = field(default_factory=list)

    def get_info(self) -> dict:
        raise NotImplementedError

    def update_info(self, name: str, species: str, breed: str) -> None:
        raise NotImplementedError

    def add_task(self, task: Task) -> None:
        raise NotImplementedError

    def remove_task(self, task_id: str) -> None:
        raise NotImplementedError

    def modify_task(self, task_id: str, updates: dict) -> None:
        raise NotImplementedError

    def get_daily_tasks(self) -> list[Task]:
        raise NotImplementedError

    def display_daily_tasks(self) -> None:
        raise NotImplementedError


class Owner:
    def __init__(self, owner_id: str, name: str, contact_info: str, preferences: dict | None = None):
        self.owner_id = owner_id
        self.name = name
        self.contact_info = contact_info
        self.preferences = preferences or {}
        self.pets: list[Pet] = []

    def get_name(self) -> str:
        raise NotImplementedError

    def get_preferences(self) -> dict:
        raise NotImplementedError

    def update_preferences(self, prefs: dict) -> None:
        raise NotImplementedError

    def add_pet(self, pet: Pet) -> None:
        raise NotImplementedError

    def remove_pet(self, pet_id: str) -> None:
        raise NotImplementedError

    def get_pets(self) -> list[Pet]:
        raise NotImplementedError


class Scheduler:
    def __init__(self, available_time_minutes: int, constraints: dict | None = None):
        self.available_time_minutes = available_time_minutes
        self.constraints = constraints or {}

    def generate_daily_plan(self, pet: Pet, owner: Owner) -> list[Task]:
        raise NotImplementedError

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        raise NotImplementedError

    def filter_by_time(self, tasks: list[Task], available_time: int) -> list[Task]:
        raise NotImplementedError

    def resolve_conflicts(self, tasks: list[Task]) -> list[Task]:
        raise NotImplementedError

    def explain_plan(self, plan: list[Task]) -> str:
        raise NotImplementedError
