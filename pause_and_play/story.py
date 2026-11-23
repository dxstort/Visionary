"""Which story to render: STORY=<module> (default `shots`, the Pause & Play story).

Every story module defines SHOTS = [(num, dur, caption text, fn(t, dur) -> Scene), ...] and may
load narration timing with load_timing().
"""
import importlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = os.environ.get("STORY", "shots")


def load_timing(shots, filename):
    """Apply a voice_align.py timing file: per-shot durations and spoken word onsets for captions.
    Skipped when NO_VOICE_TIMING is set (voice_align.py aligns against the shot list's own text)."""
    path = os.path.join(HERE, filename)
    if os.environ.get("NO_VOICE_TIMING") or not os.path.exists(path):
        return shots, {}
    timing = {int(k): v for k, v in json.load(open(path)).items()}
    shots = [(n, timing[n]["dur"], txt, fn) if n in timing else (n, d, txt, fn) for n, d, txt, fn in shots]
    return shots, {n: [(t, w) for t, w in v["words"]] for n, v in timing.items()}


def out_name(base):
    """out/<base> for the default story, out/<story>_<base> otherwise."""
    return os.path.join(HERE, "out", base if NAME == "shots" else f"{NAME}_{base}")


mod = importlib.import_module(NAME)
SHOTS = mod.SHOTS
WORD_TIMES = getattr(mod, "WORD_TIMES", {})
TIMING_FILE = getattr(mod, "TIMING_FILE", "voice_timing.json")
