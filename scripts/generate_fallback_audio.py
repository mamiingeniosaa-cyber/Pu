"""Genera audio provisional cuando faltan WAV originales.
En publicación definitiva, sustituir estos archivos por los WAV proporcionados
por la autora. Nunca sobrescribe recursos existentes.
"""
import math
import random
import struct
import wave
from pathlib import Path

DEST = Path("www")
RATE = 16000

def create(name, seconds, kind):
    target = DEST / (name + ".wav")
    if target.exists():
        print("Audio original conservado:", target)
        return
    rng = random.Random({"rain": 71, "ocean": 29, "music": 11}[kind])
    low = 0.0
    phase = 0.0
    freqs = [196.0, 246.94, 293.66]
    print("Generando audio provisional:", target)
    with wave.open(str(target), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(RATE)
        block = bytearray()
        for n in range(RATE * seconds):
            t = n / RATE
            noise = rng.uniform(-1.0, 1.0)
            low = low * .992 + noise * .008
            if kind == "rain":
                sample = noise * .10 + low * .48
            elif kind == "ocean":
                wave_env = .18 + .75 * (.5 - .5 * math.cos(2 * math.pi * t / 7.2))
                sample = (noise * .045 + low * .9) * wave_env
            else:
                volume = .5 - .5 * math.cos(2 * math.pi * min(t, seconds-t) / 4) if t < 2 or t > seconds-2 else 1
                sample = volume * sum(math.sin(2 * math.pi * f * t) for f in freqs) * .055
            value = max(-32760, min(32760, round(sample * 32767)))
            block.extend(struct.pack("<h", value))
            if len(block) >= 65536:
                out.writeframesraw(block)
                block.clear()
        if block:
            out.writeframesraw(block)

DEST.mkdir(exist_ok=True)
create("rain", 24, "rain")
create("ocean", 35, "ocean")
create("music", 24, "music")
