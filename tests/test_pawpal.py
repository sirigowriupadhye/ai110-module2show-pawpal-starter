from pawpal_system import Pet, Task


def test_mark_complete_changes_status():
    task = Task("Morning walk", "07:30")

    # A new task starts out not completed (the default is False).
    assert task.completed is False

    task.mark_complete()

    # After mark_complete(), the task is recorded as done.
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")

    # A new pet has no tasks yet.
    assert len(pet.tasks) == 0

    pet.add_task(Task("Breakfast", "08:00"))

    # One task added, so the count goes from 0 to 1.
    assert len(pet.tasks) == 1
