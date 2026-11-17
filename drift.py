"""The pool drifting on a moving sea, drawn live in the terminal until a key is pressed."""

import curses
import math
import time

SPEED = {"calm": 1.0, "storm": 3.0, "fog": 0.5, "ice": 0.0}


def wave_row(width, t, weather):
    return "".join("~" if math.sin(x / 4 + t * SPEED[weather]) > 0.3 else " " for x in range(width))


def placed(row, x, word):
    return (row[:x] + word + row[x + len(word):])[:len(row)]


def word_spot(i, word, t, weather, width, sea):
    x = int(i * 13 + t * SPEED[weather] * 2) % max(1, width - len(word))
    y = sea - 2 - i % 3 + round(math.sin(t * SPEED[weather] + i))
    return x, max(0, y)


def frame(words, t, weather, width, height):
    sea = height // 2
    rows = [" " * width] * sea + [wave_row(width, t + depth, weather) for depth in range(height - sea)]
    for i, word in enumerate(words):
        x, y = word_spot(i, word, t, weather, width, sea)
        rows[y] = placed(rows[y], x, word)
    return rows


def watch(screen, words, weather):
    screen.nodelay(True)
    curses.curs_set(0)
    start = time.monotonic()
    while screen.getch() == -1:
        height, width = screen.getmaxyx()
        for y, row in enumerate(frame(words, time.monotonic() - start, weather, width - 1, height - 1)):
            screen.addstr(y, 0, row)
        screen.refresh()
        time.sleep(0.12)


def drift(words, weather):
    curses.wrapper(watch, words, weather)
