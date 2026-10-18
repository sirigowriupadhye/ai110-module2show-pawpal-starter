from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


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


def _owner_with_pet(*tasks):
    pet = Pet("Mochi", "dog")
    for task in tasks:
        pet.add_task(task)
    owner = Owner("Jordan")
    owner.add_pet(pet)
    return Scheduler(owner), pet


def test_daily_task_creates_next_day_occurrence():
    task = Task("Walk", "07:30", "daily", due_date=date(2026, 1, 31))
    scheduler, pet = _owner_with_pet(task)

    new_task = scheduler.complete_task(pet, task)

    # Original stays completed; a separate, incomplete copy is due next day.
    assert task.completed is True
    assert new_task is not task
    assert new_task.completed is False
    assert new_task.due_date == date(2026, 2, 1)  # month rollover
    assert (new_task.description, new_task.time) == ("Walk", "07:30")
    assert pet.get_tasks() == [task, new_task]


def test_weekly_task_creates_occurrence_seven_days_later():
    task = Task("Bath", "10:00", "weekly", due_date=date(2026, 12, 28))
    scheduler, pet = _owner_with_pet(task)

    new_task = scheduler.complete_task(pet, task)

    assert new_task.due_date == date(2027, 1, 4)  # year rollover


def test_once_task_does_not_repeat():
    task = Task("Vet visit", "09:00", "once")
    scheduler, pet = _owner_with_pet(task)

    assert scheduler.complete_task(pet, task) is None
    assert task.completed is True
    assert len(pet.get_tasks()) == 1


def test_completing_twice_does_not_add_duplicate():
    task = Task("Walk", "07:30", "daily")
    scheduler, pet = _owner_with_pet(task)

    scheduler.complete_task(pet, task)
    scheduler.complete_task(pet, task)

    assert len(pet.get_tasks()) == 2


def test_new_occurrence_goes_to_the_correct_pet():
    walk = Task("Walk", "07:30", "daily")
    scheduler, mochi = _owner_with_pet(walk)
    luna = Pet("Luna", "cat")
    scheduler.owner.add_pet(luna)

    scheduler.complete_task(mochi, walk)

    assert len(mochi.get_tasks()) == 2
    assert len(luna.get_tasks()) == 0


def test_sort_by_time_orders_by_date_then_time():
    pet = Pet("Mochi", "dog")
    tomorrow_early = Task("Walk", "07:30", due_date=date(2026, 10, 18))
    today_late = Task("Play", "18:00", due_date=date(2026, 10, 17))
    today_early = Task("Feed", "08:00", due_date=date(2026, 10, 17))
    for task in (tomorrow_early, today_late, today_early):
        pet.add_task(task)
    owner = Owner("Jordan")
    owner.add_pet(pet)

    assert Scheduler(owner).sort_by_time() == [today_early, today_late, tomorrow_early]


def test_task_marked_complete_directly_still_gets_next_occurrence():
    task = Task("Walk", "07:30", "daily", due_date=date(2026, 10, 17))
    scheduler, pet = _owner_with_pet(task)
    task.mark_complete()

    new_task = scheduler.complete_task(pet, task)

    assert new_task.due_date == date(2026, 10, 18)
    assert len(pet.get_tasks()) == 2


def test_no_duplicate_even_after_next_occurrence_is_completed():
    task = Task("Walk", "07:30", "daily", due_date=date(2026, 10, 17))
    scheduler, pet = _owner_with_pet(task)

    next_task = scheduler.complete_task(pet, task)
    next_task.mark_complete()  # tomorrow's task finished some other way
    assert scheduler.complete_task(pet, task) is None

    assert len(pet.get_tasks()) == 2


def test_detect_conflicts_across_pets():
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    today = date(2026, 10, 17)
    mochi.add_task(Task("Grooming", "09:00", due_date=today))
    luna.add_task(Task("Vet call", "09:00", due_date=today))
    luna.add_task(Task("Breakfast", "08:00", due_date=today))
    owner = Owner("Jordan")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    warnings = Scheduler(owner).detect_conflicts()

    assert warnings == [
        "Conflict on 2026-10-17 at 09:00: Mochi - Grooming, Luna - Vet call"
    ]


def test_detect_conflicts_ignores_other_dates_completed_and_empty():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", "09:00", due_date=date(2026, 10, 17)))
    pet.add_task(Task("Play", "09:00", due_date=date(2026, 10, 18)))  # other day
    done = Task("Feed", "09:00", due_date=date(2026, 10, 17))
    done.mark_complete()  # finished, so it no longer conflicts
    pet.add_task(done)
    owner = Owner("Jordan")
    owner.add_pet(pet)

    assert Scheduler(owner).detect_conflicts() == []
    assert Scheduler(Owner("Nobody")).detect_conflicts() == []


def test_detect_conflicts_three_tasks_one_warning():
    pet = Pet("Mochi", "dog")
    for name in ("A", "B", "C"):
        pet.add_task(Task(name, "10:00"))
    owner = Owner("Jordan")
    owner.add_pet(pet)

    assert len(Scheduler(owner).detect_conflicts()) == 1
