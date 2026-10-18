"""Command-line demo of the PawPal+ system."""

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # Create an owner and two pets.
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog", 3)
    luna = Pet("Luna", "cat", 5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Add tasks out of chronological order.
    mochi.add_task(Task("Evening play", "18:00", "daily"))
    luna.add_task(Task("Give medication", "20:15", "once"))
    mochi.add_task(Task("Morning walk", "07:30", "daily"))
    luna.add_task(Task("Breakfast", "08:00", "daily"))

    # Two tasks at the same time (on different pets) to trigger a conflict.
    mochi.add_task(Task("Grooming", "09:00", "once"))
    luna.add_task(Task("Vet call", "09:00", "once"))

    # The scheduler gets every task through the owner.
    scheduler = Scheduler(owner)
    tasks = scheduler.get_all_tasks()

    # Remember which pet each task belongs to, just for printing.
    pet_for_task = {id(task): pet.name for pet in owner.pets for task in pet.get_tasks()}

    # Sort by time ("HH:MM" strings sort correctly as plain text).
    tasks = scheduler.sort_by_time()

    print(f"Today's Schedule for {owner.name}")
    print("=" * 40)
    for task in tasks:
        status = "done" if task.completed else "to do"
        print(f"{task.time}  {pet_for_task[id(task)]:<6} {task.description} ({task.frequency}) [{status}]")

    # Warn about tasks scheduled at the same time (across all pets).
    print()
    print("Conflict check")
    print("-" * 40)
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"WARNING: {warning}")
    else:
        print("No scheduling conflicts.")

    # Complete Luna's daily "Breakfast". This marks it done and, because it
    # repeats, adds a new Breakfast for tomorrow to Luna's tasks.
    breakfast = next(t for t in luna.get_tasks() if t.description == "Breakfast")
    next_breakfast = scheduler.complete_task(luna, breakfast)
    print()
    print(f"Completed '{breakfast.description}' ({breakfast.due_date}); "
          f"next one added for {next_breakfast.due_date}")

    # Rebuild the lookup so it includes the newly added task.
    pet_for_task = {id(task): pet.name for pet in owner.pets for task in pet.get_tasks()}

    # Filter by pet name only.
    print()
    print("Filter: Mochi's tasks (pet_name='Mochi')")
    print("-" * 40)
    for task in scheduler.filter_tasks(pet_name="Mochi"):
        print(f"{task.time}  {task.description}")

    # Filter by completion status only.
    print()
    print("Filter: incomplete tasks (completed=False)")
    print("-" * 40)
    for task in scheduler.filter_tasks(completed=False):
        print(f"{task.time}  {pet_for_task[id(task)]:<6} {task.description}")

    # Both filters together.
    print()
    print("Filter: Luna's incomplete tasks (pet_name='Luna', completed=False)")
    print("-" * 40)
    for task in scheduler.filter_tasks(pet_name="Luna", completed=False):
        print(f"{task.time}  {task.description}")


if __name__ == "__main__":
    main()
