"""Command-line demo of the PawPal+ system."""

import os
import sys
import unicodedata

from pawpal_system import Owner, Pet, Task, Scheduler

# Color only when printing to a real terminal (and the user hasn't set NO_COLOR).
USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ
if USE_COLOR and os.name == "nt":
    os.system("")  # turns on ANSI color support in the Windows console

BOLD, RED, GREEN, YELLOW, CYAN = "1", "31", "32", "33", "36"


def colorize(text: str, code: str) -> str:
    """Wrap text in an ANSI color code (no-op when color is off)."""
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def display_width(text: str) -> int:
    """Return how many terminal columns text takes (emojis are 2 wide)."""
    width = 0
    for char in text:
        if unicodedata.combining(char) or char in "️‍":
            continue
        width += 2 if unicodedata.east_asian_width(char) in ("W", "F") else 1
    return width


def pad(text: str, width: int) -> str:
    """Left-align text in a column of the given display width."""
    return text + " " * (width - display_width(text))


def get_pet_emoji(species: str) -> str:
    """Return an emoji based on the pet's species."""
    species = species.lower()
    if species == "dog":
        return "🐕"
    elif species == "cat":
        return "🐈"
    else:
        return "🐾"


def get_task_emoji(description: str) -> str:
    """Return an emoji based on the task description."""
    description = description.lower()

    if "walk" in description:
        return "🚶"
    elif "feed" in description or "breakfast" in description:
        return "🍖"
    elif "medication" in description or "medicine" in description:
        return "💊"
    elif "play" in description:
        return "🎾"
    elif "groom" in description or "bath" in description:
        return "🛁"
    elif "vet" in description:
        return "🩺"
    else:
        return "📋"


def print_heading(title: str) -> None:
    """Print a bold section title with an underline."""
    print()
    print(colorize(title, BOLD))
    print("-" * display_width(title))


def print_task_table(tasks, pet_for_task) -> None:
    """Print tasks as a bordered table with emojis and a color-coded status."""
    headers = ["Time", "Pet", "Task", "Frequency", "Status"]

    # Each cell is (text, color); the color is applied after padding so the
    # invisible color codes never throw off the column widths.
    rows = []
    for task in tasks:
        pet = pet_for_task[id(task)]
        status = ("✅ Done", GREEN) if task.completed else ("⏳ To do", YELLOW)
        rows.append([
            (task.time, CYAN),
            (f"{get_pet_emoji(pet.species)} {pet.name}", None),
            (f"{get_task_emoji(task.description)} {task.description}", None),
            (task.frequency, None),
            status,
        ])

    if not rows:
        print("(no tasks)")
        return

    widths = [
        max([display_width(headers[i])] + [display_width(row[i][0]) for row in rows])
        for i in range(len(headers))
    ]

    def print_row(cells):
        shown = [
            colorize(pad(text, widths[i]), color) if color else pad(text, widths[i])
            for i, (text, color) in enumerate(cells)
        ]
        print("| " + " | ".join(shown) + " |")

    border = "+-" + "-+-".join("-" * width for width in widths) + "-+"
    print(border)
    print_row([(header, BOLD) for header in headers])
    print(border)
    for row in rows:
        print_row(row)
    print(border)


def main() -> None:
    # Emojis need UTF-8; the default Windows encoding can't print them.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

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

    # Remember which pet owns each task, just for printing.
    pet_for_task = {id(task): pet for pet in owner.pets for task in pet.get_tasks()}

    # Sort by due date, then time.
    tasks = scheduler.sort_by_time()

    print_heading(f"🐾 Today's Schedule for {owner.name}")
    print_task_table(tasks, pet_for_task)

    # Warn about tasks scheduled at the same time (across all pets).
    print_heading("🔎 Conflict check")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(colorize(f"🚨 WARNING: {warning}", RED))
    else:
        print(colorize("✅ No scheduling conflicts.", GREEN))

    # Complete Luna's daily "Breakfast". This marks it done and, because it
    # repeats, adds a new Breakfast for tomorrow to Luna's tasks.
    breakfast = next(t for t in luna.get_tasks() if t.description == "Breakfast")
    next_breakfast = scheduler.complete_task(luna, breakfast)
    print()
    print(colorize(
        f"✅ Completed '{breakfast.description}' ({breakfast.due_date}); "
        f"next one added for {next_breakfast.due_date}",
        GREEN,
    ))

    # Rebuild the lookup so it includes the newly added task.
    pet_for_task = {id(task): pet for pet in owner.pets for task in pet.get_tasks()}

    # Filter by pet name only.
    print_heading("🐕 Filter: Mochi's tasks (pet_name='Mochi')")
    print_task_table(scheduler.filter_tasks(pet_name="Mochi"), pet_for_task)

    # Filter by completion status only.
    print_heading("⏳ Filter: incomplete tasks (completed=False)")
    print_task_table(scheduler.filter_tasks(completed=False), pet_for_task)

    # Both filters together.
    print_heading("🐈 Filter: Luna's incomplete tasks (pet_name='Luna', completed=False)")
    print_task_table(
        scheduler.filter_tasks(pet_name="Luna", completed=False), pet_for_task
    )


if __name__ == "__main__":
    main()
