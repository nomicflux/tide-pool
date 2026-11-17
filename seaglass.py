"""Render words as small glass bells over the surf, using only the Python standard library."""

import math
import random
import struct
import wave

RATE = 16000
DURATION = {"calm": 0.5, "storm": 0.22, "fog": 0.8, "ice": 1.1}
SURF = {"calm": 1500, "fog": 3000, "storm": 9000, "ice": 400}
SCALE = (0, 2, 4, 7, 9)


def pitch(word):
    degree = sum(ord(letter) for letter in word.casefold()) % 10
    semitone = SCALE[degree % 5] + 12 * (degree // 5)
    return 220 * 2 ** (semitone / 12)


def sample(frequency, duration, t):
    envelope = min(t / 0.01, 1) * math.exp(-6 * t / duration)
    tone = (math.sin(2 * math.pi * frequency * t)
            + 0.3 * math.sin(2 * math.pi * frequency * 2.01 * t))
    return int(10000 * envelope * tone)


def surf(word, count, level):
    rng, smooth, wash = random.Random(word), 0.0, []
    for i in range(count):
        smooth += 0.05 * (rng.uniform(-1, 1) - smooth)
        swell = 0.5 - 0.5 * math.cos(2 * math.pi * i / count)
        wash.append(int(level * swell * smooth))
    return wash


def bell(frequency, duration, wash):
    count = int(RATE * duration)
    return struct.pack(f"<{count}h", *(sample(frequency, duration, i / RATE) + wash[i]
                                       for i in range(count)))


def chime(word, weather):
    count = int(RATE * DURATION[weather])
    return bell(pitch(word), DURATION[weather], surf(word, count, SURF[weather]))


def tone(frequency, seconds):
    count, fade = int(RATE * seconds), int(RATE * 0.005)
    return struct.pack(f"<{count}h", *(int(8000 * min(1, i / fade, (count - i) / fade)
                                           * math.sin(2 * math.pi * frequency * i / RATE))
                                       for i in range(count)))


def rest(seconds):
    return bytes(2 * int(RATE * seconds))


def record(path, frames):
    with wave.open(str(path), "wb") as song:
        song.setnchannels(1)
        song.setsampwidth(2)
        song.setframerate(RATE)
        for frame in frames:
            song.writeframes(frame)


def sing(words, weather, path):
    record(path, (chime(word, weather) for word in words))


def recited(line):
    return b"".join(chime(word, "calm") for word in line.split()) + rest(0.4)


def recite(lines, path):
    record(path, map(recited, lines))
