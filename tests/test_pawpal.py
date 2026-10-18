from datetime import date

import pytest

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


# ---------------------------------------------------------------------------
# Empty-data edge cases
# ---------------------------------------------------------------------------

def test_owner_with_no_pets_returns_empty_results():
    scheduler = Scheduler(Owner("Jordan"))

    # With no pets there is nothing to gather, sort, filter, or conflict.
    assert scheduler.get_all_tasks() == []
    assert scheduler.sort_by_time() == []
    assert scheduler.filter_tasks() == []
    assert scheduler.filter_tasks(pet_name="Mochi", completed=False) == []
    assert scheduler.detect_conflicts() == []


def test_pet_with_no_tasks_returns_empty_results():
    scheduler, pet = _owner_with_pet()  # one pet, zero tasks

    # The pet exists, so filtering by its name works but finds nothing.
    assert pet.get_tasks() == []
    assert scheduler.sort_by_time() == []
    assert scheduler.filter_tasks(pet_name="Mochi") == []
    assert scheduler.detect_conflicts() == []


def test_empty_pet_does_not_hide_another_pets_tasks():
    scheduler, _ = _owner_with_pet()  # Mochi has no tasks
    luna = Pet("Luna", "cat")
    feed = Task("Breakfast", "08:00")
    luna.add_task(feed)
    scheduler.owner.add_pet(luna)

    # Only Luna's task comes back; the empty pet contributes nothing.
    assert scheduler.get_all_tasks() == [feed]


def test_remove_task_not_on_pet_raises_value_error():
    pet = Pet("Mochi", "dog")

    # Pet.remove_task uses list.remove, so a missing task raises ValueError.
    with pytest.raises(ValueError):
        pet.remove_task(Task("Walk", "07:30"))


# ---------------------------------------------------------------------------
# Chronological sorting
# ---------------------------------------------------------------------------

def test_sort_by_time_orders_same_day_tasks_by_clock_time():
    today = date(2026, 10, 17)
    evening = Task("Play", "18:00", due_date=today)
    morning = Task("Walk", "07:30", due_date=today)
    mid = Task("Meds", "09:05", due_date=today)
    scheduler, _ = _owner_with_pet(evening, morning, mid)

    # Added out of order; sorted result runs earliest to latest.
    assert scheduler.sort_by_time() == [morning, mid, evening]


def test_sort_by_time_merges_tasks_from_multiple_pets():
    today = date(2026, 10, 17)
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    late = Task("Walk", "17:00", due_date=today)
    early = Task("Breakfast", "06:45", due_date=today)
    middle = Task("Litter", "12:00", due_date=today)
    mochi.add_task(late)
    luna.add_task(early)
    luna.add_task(middle)
    owner = Owner("Jordan")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # One list sorted across pets, not grouped per pet.
    assert Scheduler(owner).sort_by_time() == [early, middle, late]


def test_sort_by_time_handles_midnight_and_last_minute():
    today = date(2026, 10, 17)
    last = Task("Night check", "23:59", due_date=today)
    first = Task("Midnight meds", "00:00", due_date=today)
    scheduler, _ = _owner_with_pet(last, first)

    assert scheduler.sort_by_time() == [first, last]


def test_sort_by_time_is_stable_for_identical_times():
    today = date(2026, 10, 17)
    first_added = Task("A", "09:00", due_date=today)
    second_added = Task("B", "09:00", due_date=today)
    scheduler, _ = _owner_with_pet(first_added, second_added)

    result = scheduler.sort_by_time()

    # Equal keys keep insertion order (identity check: the tasks compare equal
    # only if all fields match, and these differ by description anyway).
    assert result[0] is first_added
    assert result[1] is second_added


def test_sort_by_time_does_not_reorder_the_pets_own_list():
    today = date(2026, 10, 17)
    late = Task("Play", "18:00", due_date=today)
    early = Task("Walk", "07:30", due_date=today)
    scheduler, pet = _owner_with_pet(late, early)

    result = scheduler.sort_by_time()

    # sorted() builds a new list, so the pet keeps its original order.
    assert result is not pet.get_tasks()
    assert pet.get_tasks() == [late, early]


# ---------------------------------------------------------------------------
# Daily / recurring tasks
# ---------------------------------------------------------------------------

def test_daily_recurrence_handles_leap_day():
    task = Task("Walk", "07:30", "daily", due_date=date(2028, 2, 28))
    scheduler, pet = _owner_with_pet(task)

    new_task = scheduler.complete_task(pet, task)

    # 2028 is a leap year, so the day after Feb 28 is Feb 29.
    assert new_task.due_date == date(2028, 2, 29)


def test_next_occurrence_leaves_original_untouched():
    task = Task("Walk", "07:30", "daily", due_date=date(2026, 10, 17))

    new_task = task.next_occurrence()

    # next_occurrence only builds a copy; it does not complete or move the original.
    assert task.completed is False
    assert task.due_date == date(2026, 10, 17)
    assert new_task is not task
    assert new_task.due_date == date(2026, 10, 18)
    assert new_task.frequency == "daily"


def test_unknown_frequency_does_not_repeat():
    for frequency in ("monthly", "Daily", ""):
        task = Task("Walk", "07:30", frequency, due_date=date(2026, 10, 17))
        scheduler, pet = _owner_with_pet(task)

        # Only the exact strings "daily" and "weekly" repeat.
        assert task.next_occurrence() is None
        assert scheduler.complete_task(pet, task) is None
        assert len(pet.get_tasks()) == 1


def test_daily_chain_advances_one_day_each_time():
    task = Task("Walk", "07:30", "daily", due_date=date(2026, 10, 17))
    scheduler, pet = _owner_with_pet(task)

    second = scheduler.complete_task(pet, task)
    third = scheduler.complete_task(pet, second)

    # Completing each new occurrence keeps the chain going.
    assert [t.due_date for t in pet.get_tasks()] == [
        date(2026, 10, 17),
        date(2026, 10, 18),
        date(2026, 10, 19),
    ]
    assert third.completed is False


def test_existing_matching_task_prevents_duplicate_occurrence():
    task = Task("Walk", "07:30", "daily", due_date=date(2026, 10, 17))
    already_there = Task("Walk", "07:30", "daily", due_date=date(2026, 10, 18))
    scheduler, pet = _owner_with_pet(task, already_there)

    # Tomorrow's walk was added manually, so no second copy is created.
    assert scheduler.complete_task(pet, task) is None
    assert len(pet.get_tasks()) == 2


def test_complete_task_for_wrong_pet_raises_and_changes_nothing():
    task = Task("Walk", "07:30", "daily")
    scheduler, mochi = _owner_with_pet(task)
    luna = Pet("Luna", "cat")
    scheduler.owner.add_pet(luna)

    with pytest.raises(ValueError):
        scheduler.complete_task(luna, task)

    # The ownership check runs before anything is modified.
    assert task.completed is False
    assert len(mochi.get_tasks()) == 1
    assert luna.get_tasks() == []


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_within_a_single_pet():
    today = date(2026, 10, 17)
    scheduler, _ = _owner_with_pet(
        Task("Walk", "09:00", due_date=today),
        Task("Feed", "09:00", due_date=today),
    )

    # Same pet, same slot: still a conflict, and the pet is named for each task.
    assert scheduler.detect_conflicts() == [
        "Conflict on 2026-10-17 at 09:00: Mochi - Walk, Mochi - Feed"
    ]


def test_detect_conflicts_reports_each_slot_in_chronological_order():
    today = date(2026, 10, 17)
    scheduler, _ = _owner_with_pet(
        Task("Late A", "15:00", due_date=today),
        Task("Late B", "15:00", due_date=today),
        Task("Early A", "08:00", due_date=today),
        Task("Early B", "08:00", due_date=today),
    )

    warnings = scheduler.detect_conflicts()

    # Two conflicting slots give two warnings, earliest slot first.
    assert len(warnings) == 2
    assert "at 08:00" in warnings[0]
    assert "at 15:00" in warnings[1]


def test_detect_conflicts_ignores_near_misses_and_all_completed():
    today = date(2026, 10, 17)
    done_a = Task("A", "11:00", due_date=today)
    done_b = Task("B", "11:00", due_date=today)
    done_a.mark_complete()
    done_b.mark_complete()
    scheduler, _ = _owner_with_pet(
        Task("Walk", "09:00", due_date=today),
        Task("Feed", "09:05", due_date=today),  # 5 minutes apart: not exact
        done_a,
        done_b,  # both finished, so no longer a conflict
    )

    # Only exact date+time matches among unfinished tasks count.
    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_does_not_modify_tasks():
    today = date(2026, 10, 17)
    a = Task("A", "10:00", due_date=today)
    b = Task("B", "10:00", due_date=today)
    scheduler, pet = _owner_with_pet(a, b)

    scheduler.detect_conflicts()

    # Detection is read-only: same tasks, same order, still unfinished.
    assert pet.get_tasks() == [a, b]
    assert not a.completed and not b.completed


def test_new_daily_occurrence_does_not_conflict_with_original():
    task = Task("Walk", "07:30", "daily", due_date=date(2026, 10, 17))
    scheduler, pet = _owner_with_pet(task)

    scheduler.complete_task(pet, task)

    # The original is done and the copy is on a different day.
    assert scheduler.detect_conflicts() == []


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def test_filter_tasks_by_pet_and_completion():
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    mochi_done = Task("Walk", "07:00")
    mochi_done.mark_complete()
    mochi_open = Task("Feed", "08:00")
    luna_open = Task("Litter", "09:00")
    mochi.add_task(mochi_done)
    mochi.add_task(mochi_open)
    luna.add_task(luna_open)
    owner = Owner("Jordan")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    scheduler = Scheduler(owner)

    assert scheduler.filter_tasks() == [mochi_done, mochi_open, luna_open]
    assert scheduler.filter_tasks(pet_name="Luna") == [luna_open]
    assert scheduler.filter_tasks(completed=False) == [mochi_open, luna_open]
    assert scheduler.filter_tasks(pet_name="Mochi", completed=True) == [mochi_done]
    assert scheduler.filter_tasks(pet_name="Nobody") == []


def test_filter_by_pet_uses_identity_for_equal_tasks():
    # Two pets with tasks that are equal field-for-field (dataclass ==).
    day = date(2026, 10, 17)
    mochi_task = Task("Feed", "08:00", due_date=day)
    luna_task = Task("Feed", "08:00", due_date=day)
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    mochi.add_task(mochi_task)
    luna.add_task(luna_task)
    owner = Owner("Jordan")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    result = Scheduler(owner).filter_tasks(pet_name="Luna")

    # Exactly one task, and it is Luna's object, not Mochi's.
    assert len(result) == 1
    assert result[0] is luna_task
