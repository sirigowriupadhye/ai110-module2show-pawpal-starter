"""PawPal+ system skeleton: Owner, Pet, Task, and Scheduler.

Matches diagrams/uml_draft.mmd. Scheduling algorithms are stubs for now.
"""

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from typing import List, Optional


@dataclass
class Task:
    """A single pet-care activity (e.g. a walk or feeding)."""

    description: str
    time: str  # "HH:MM", 24-hour, e.g. "08:30"
    frequency: str = "once"  # e.g. "once", "daily", "weekly"
    completed: bool = False
    due_date: date = field(default_factory=date.today)  # day this task is due

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self) -> Optional["Task"]:
        """Return a new Task for the next time this task is due, or None.

        "daily" tasks come back one day later and "weekly" tasks seven days
        later, counted from this task's due_date (timedelta handles month and
        year rollover). "once" tasks don't repeat, so they return None.
        The new task is a separate object and starts out not completed;
        this task is left unchanged.
        """
        if self.frequency == "daily":
            interval = timedelta(days=1)
        elif self.frequency == "weekly":
            interval = timedelta(weeks=1)
        else:
            return None
        return replace(self, completed=False, due_date=self.due_date + interval)


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

    def complete_task(self, pet: Pet, task: Task) -> Optional[Task]:
        """Mark a pet's task complete and schedule its next occurrence.

        The caller passes the Pet that owns the task. The task is marked
        complete, then Task.next_occurrence() builds the follow-up for daily
        and weekly tasks, which is added to that same pet with Pet.add_task().
        Returns the new task, or None if the task doesn't repeat or was
        that occurrence already exists on the pet, so processing the same task
        more than once never adds a duplicate. Raises ValueError if the task
        doesn't belong to the given pet.
        """
        if not any(existing is task for existing in pet.get_tasks()):
            raise ValueError(f"That task does not belong to {pet.name}.")

        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is None:
            return None

        # Same description, time, frequency and due date means the next
        # occurrence is already scheduled (even if it has since been completed).
        already_scheduled = any(
            existing.description == next_task.description
            and existing.time == next_task.time
            and existing.frequency == next_task.frequency
            and existing.due_date == next_task.due_date
            for existing in pet.get_tasks()
        )
        if already_scheduled:
            return None

        pet.add_task(next_task)
        return next_task

    def get_todays_schedule(self) -> List[Task]:
        """Return the tasks planned for today."""
        # TODO: decide how "today" is determined (frequency + time) and filter.
        raise NotImplementedError

    def sort_by_time(self) -> List[Task]:
        """Return all of the owner's tasks in chronological order.

        Tasks are fetched through Owner.get_all_tasks() and sorted by due date
        first, then by their "HH:MM" time, so tomorrow's 07:30 task comes after
        today's 18:00 task. Because times are zero-padded 24-hour strings,
        comparing them as text gives the same order as comparing clock times.
        Returns a new list; the pets' own task lists are not reordered.
        """
        return sorted(
            self.owner.get_all_tasks(), key=lambda task: (task.due_date, task.time)
        )

    def filter_tasks(
        self, pet_name: Optional[str] = None, completed: Optional[bool] = None
    ) -> List[Task]:
        """Return tasks filtered by pet name and/or completion status.

        Starts from Owner.get_all_tasks() and keeps only the tasks that match
        every filter that was given:
          - pet_name: only tasks belonging to the pet with this Pet.name.
          - completed: True keeps finished tasks, False keeps unfinished ones.
        A filter left as None is ignored, so passing neither returns every task.

        Returns a new list; the original tasks and pets are not changed.
        """
        tasks = self.owner.get_all_tasks()

        if pet_name is not None:
            # Tasks don't know their pet, so collect the named pet's tasks
            # and keep only those (compared by identity, not by equal values).
            pet_task_ids = {
                id(task)
                for pet in self.owner.pets
                if pet.name == pet_name
                for task in pet.get_tasks()
            }
            tasks = [task for task in tasks if id(task) in pet_task_ids]

        if completed is not None:
            tasks = [task for task in tasks if task.completed == completed]

        return tasks

    def detect_conflicts(self) -> List[str]:
        """Return a warning message for each time slot with 2+ tasks.

        Tasks come from Owner.get_all_tasks(), so conflicts are found across
        all of the owner's pets (and within a single pet). Tasks conflict when
        they share the same due date and "HH:MM" time; completed tasks are
        ignored. Only exact matches are caught, since tasks have no duration.

        Returns a list of readable warnings such as
        "Conflict on 2026-10-17 at 09:00: Mochi - Grooming, Luna - Vet call".
        The list is empty when nothing conflicts. Nothing is raised or changed.
        """
        # Tasks don't know their pet, so map each task to its pet's name.
        pet_for_task = {
            id(task): pet.name for pet in self.owner.pets for task in pet.get_tasks()
        }

        # Group unfinished tasks by (due date, time).
        slots = {}
        for task in self.owner.get_all_tasks():
            if not task.completed:
                slots.setdefault((task.due_date, task.time), []).append(task)

        warnings: List[str] = []
        for (due_date, time), tasks in sorted(slots.items()):
            if len(tasks) > 1:
                details = ", ".join(
                    f"{pet_for_task.get(id(task), 'Unknown pet')} - {task.description}"
                    for task in tasks
                )
                warnings.append(f"Conflict on {due_date} at {time}: {details}")
        return warnings
