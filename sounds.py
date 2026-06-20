import numpy as np
import sounddevice as sd


def _play(freq, duration, volume=0.15):
    sr = 22050
    t = np.linspace(0, duration, int(sr * duration), False)
    env = np.exp(-t * 10)
    tone = np.sin(freq * 2 * np.pi * t) * env * volume
    sd.play(tone, sr, blocking=False)


def _play_chord(notes, note_duration, volume=0.12):
    sr = 22050
    gap = 0.04
    total_len = int(sr * (len(notes) * (note_duration + gap)))
    total = np.zeros(total_len)
    for i, freq in enumerate(notes):
        n = int(sr * note_duration)
        start = int(sr * i * (note_duration + gap))
        t = np.linspace(0, note_duration, n, False)
        env = np.exp(-t * 6)
        tone = np.sin(freq * 2 * np.pi * t) * env * volume
        total[start : start + n] += tone
    sd.play(total, sr, blocking=False)


def record_start():
    _play(800, 0.04)


def record_stop():
    _play(400, 0.05)


def transcribed():
    _play_chord([523, 659, 784], 0.08)


def error():
    _play(200, 0.15, 0.1)
