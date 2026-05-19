"""Sound effects — generates simple tones if .wav files are absent."""
import pygame
import warnings
import struct
import math


_sounds: dict = {}
_enabled = False


def init_sounds() -> None:
    global _enabled
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        _enabled = True
    except Exception as exc:
        warnings.warn(f"Sound init failed: {exc}")
        return

    sound_map = {
        "click":   ("assets/sounds/click.wav",   _gen_click),
        "correct": ("assets/sounds/correct.wav", _gen_correct),
        "wrong":   ("assets/sounds/wrong.wav",   _gen_wrong),
        "win":     ("assets/sounds/win.wav",      _gen_win),
        "badge":   ("assets/sounds/badge.wav",    _gen_badge),
    }
    for name, (path, generator) in sound_map.items():
        try:
            _sounds[name] = pygame.mixer.Sound(path)
        except Exception:
            try:
                _sounds[name] = generator()
            except Exception as exc2:
                warnings.warn(f"Could not generate sound '{name}': {exc2}")


def play(name: str, volume: float = 0.7) -> None:
    if not _enabled:
        return
    snd = _sounds.get(name)
    if snd:
        snd.set_volume(volume)
        snd.play()


# ---- Tone generators -------------------------------------------------------

def _make_tone(freq: float, duration: float, amplitude: int = 16000,
               sample_rate: int = 44100) -> pygame.mixer.Sound:
    n = int(sample_rate * duration)
    data = bytearray()
    for i in range(n):
        t = i / sample_rate
        fade = min(1.0, min(t / 0.01, (duration - t) / 0.05))
        v = int(amplitude * fade * math.sin(2 * math.pi * freq * t))
        v = max(-32768, min(32767, v))
        sample = struct.pack('<hh', v, v)
        data.extend(sample)
    return pygame.mixer.Sound(buffer=bytes(data))


def _gen_click() -> pygame.mixer.Sound:
    return _make_tone(800, 0.06, 8000)


def _gen_correct() -> pygame.mixer.Sound:
    # Simple major chord sweep
    n = int(44100 * 0.4)
    data = bytearray()
    freqs = [523.25, 659.25, 783.99]
    for i in range(n):
        t = i / 44100
        fade = min(1.0, min(t / 0.01, (0.4 - t) / 0.05))
        v = sum(int(8000 * fade * math.sin(2 * math.pi * f * t)) for f in freqs)
        v = max(-32768, min(32767, v))
        data.extend(struct.pack('<hh', v, v))
    return pygame.mixer.Sound(buffer=bytes(data))


def _gen_wrong() -> pygame.mixer.Sound:
    return _make_tone(220, 0.3, 12000)


def _gen_win() -> pygame.mixer.Sound:
    n = int(44100 * 0.8)
    data = bytearray()
    melody = [523, 659, 784, 1047]
    step = n // len(melody)
    for i in range(n):
        t = i / 44100
        fi = min(i // step, len(melody) - 1)
        fade = min(1.0, min(t / 0.01, (0.8 - t) / 0.05))
        v = int(12000 * fade * math.sin(2 * math.pi * melody[fi] * t))
        v = max(-32768, min(32767, v))
        data.extend(struct.pack('<hh', v, v))
    return pygame.mixer.Sound(buffer=bytes(data))


def _gen_badge() -> pygame.mixer.Sound:
    n = int(44100 * 0.5)
    data = bytearray()
    for i in range(n):
        t = i / 44100
        freq = 500 + 1000 * (t / 0.5)
        fade = min(1.0, min(t / 0.01, (0.5 - t) / 0.05))
        v = int(10000 * fade * math.sin(2 * math.pi * freq * t))
        v = max(-32768, min(32767, v))
        data.extend(struct.pack('<hh', v, v))
    return pygame.mixer.Sound(buffer=bytes(data))
