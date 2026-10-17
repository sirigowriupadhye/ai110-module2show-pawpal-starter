"""PawPal+ system skeleton: Owner, Pet, Task, and Scheduler.

Matches diagrams/uml_draft.mmd. Scheduling algorithms are stubs for now.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Task:
    """A single pet-care activity (e.g. a walk or feeding)."""

    description: str
    time: str  # "HH:MM", 24-hour, e.g. "08:30"
    frequency: str = "once"  # e.g. "once", "daily", "weekly"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True


@dataclass
class Pet:
    """A pet and the tasks that belong to it."""

    name: str
    species: str
    age: int = 0
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        self.tasks.remove(task)

    def get_tasks(self) -> List[Task]:
        """Return all of this pet's tasks."""
        return self.tasks


@dataclass
class Owner:
    """A person who manages one or more pets."""

    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        self.pets.remove(pet)

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of this owner's pets."""
        all_tasks: List[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks


class Scheduler:
    """Organizes tasks. Reaches them through its Owner, never directly via pets."""

    def __init__(self, owner: Owner):
        """Connect this scheduler to the owner whose tasks it will organize."""
        self.owner = owner

    def get_all_tasks(self) -> List[Task]:
        """Fetch all tasks for the owner's pets."""
        return self.owner.get_all_tasks()

    def get_todays_schedule(self) -> List[Task]:
        """Return the tasks planned for today."""
        # TODO: decide how "today" is determined (frequency + time) and filter.
        raise NotImplementedError

    def sort_by_time(self) -> List[Task]:
        """Return all tasks ordered by their time."""
        # TODO: sort self.get_all_tasks() by Task.time.
        raise NotImplementedError

    def filter_tasks(
        self, pet_name: Optional[str] = None, completed: Optional[bool] = None
    ) -> List[Task]:
        """Return tasks filtered by pet name and/or completion status."""
        # TODO: filter by pet_name and/or completed.
        raise NotImplementedError

    def detect_conflicts(self) -> List[Task]:
        """Return tasks that are scheduled at the same time."""
        # TODO: find tasks that share a time.
        raise NotImplementedError
