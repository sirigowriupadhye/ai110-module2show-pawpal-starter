"""Command-line demo of the PawPal+ system."""

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # Create an owner and two pets.
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog", 3)
    luna = Pet("Luna", "cat", 5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Add tasks with different times across the pets.
    mochi.add_task(Task("Morning walk", "07:30", "daily"))
    luna.add_task(Task("Breakfast", "08:00", "daily"))
    mochi.add_task(Task("Evening play", "18:00", "daily"))
    luna.add_task(Task("Give medication", "20:15", "once"))

    # The scheduler gets every task through the owner.
    scheduler = Scheduler(owner)
    tasks = scheduler.get_all_tasks()

    # Remember which pet each task belongs to, just for printing.
    pet_for_task = {id(task): pet.name for pet in owner.pets for task in pet.get_tasks()}

    # Sort by time ("HH:MM" strings sort correctly as plain text).
    tasks = sorted(tasks, key=lambda task: task.time)

    print(f"Today's Schedule for {owner.name}")
    print("=" * 40)
    for task in tasks:
        status = "done" if task.completed else "to do"
        print(f"{task.time}  {pet_for_task[id(task)]:<6} {task.description} ({task.frequency}) [{status}]")


if __name__ == "__main__":
    main()
