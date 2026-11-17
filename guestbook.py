"""The guestbook: one dated line for each keeper who signs it, beside the shore."""

import os


def entry(name, day):
    """One signature as written: the day, then the name on one line."""
    return f"{day} · {' '.join(name.split())}"


def sign(path, name, day):
    with open(path, "a", encoding="utf-8") as book:
        book.write(entry(name, day) + "\n")


def signatures(path):
    """Every signature, oldest first; none before anyone has signed."""
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as book:
        return book.read().splitlines()
