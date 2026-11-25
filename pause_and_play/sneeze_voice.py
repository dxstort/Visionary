"""Narration for When You SNEEZE, You SWITCH Places, made with Fish Audio (voice model eb4bcc6dbb634e9eaee239c94266935e).

    FISH_API_KEY=... python3 sneeze_voice.py        -> sneeze_voiceover.mp3

The key is read from the environment only. It is never written to a file, printed or logged.
The story is spoken in short beats (a few lines each) that are joined with a small gap, so the pacing stays natural
and one failed request only costs one beat.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

import ast  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def _lines():
    """LINES from sneeze.py, read without importing the renderer."""
    for node in ast.parse(open(os.path.join(HERE, "sneeze.py")).read()).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "LINES":
            return ast.literal_eval(node.value)


LINES = _lines()
URL = "https://api.fish.audio/v1/tts"
VOICE = "eb4bcc6dbb634e9eaee239c94266935e"
BEATS = [(0, 3), (3, 6), (6, 10), (10, 14), (14, 19), (19, 24), (24, 29), (29, 33), (33, 38), (38, 42), (42, 46)]
GAP = 0.18


def speakable(line):
    """Text for the voice: ALL-CAPS emphasis words are lower-cased so they are read, not spelled."""
    out = []
    for w in line.split():
        core = re.sub(r"[^A-Za-z']", "", w)
        if len(core) >= 2 and core.isupper() and core not in ("OK",):
            w = w.lower()
        out.append(w)
    txt = " ".join(out)
    txt = re.sub(r"\bMr\b", "Mister", txt)
    txt = re.sub(r"\bMrs\b", "Missus", txt)
    txt = txt.replace("creeeak", "creeeak,").replace("Creeeak.", "Creeeeak.")
    return txt[0].upper() + txt[1:]


def synth(text, path, key, tries=4):
    body = json.dumps({"text": text, "reference_id": VOICE, "format": "mp3"}).encode()
    req = urllib.request.Request(URL, data=body, method="POST", headers={
        "Authorization": f"Bearer {key}", "model": "s2.1-pro-free", "Content-Type": "application/json"})
    for k in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = r.read()
            if len(data) < 2000:
                raise RuntimeError(f"short audio ({len(data)} bytes)")
            open(path, "wb").write(data)
            return
        except urllib.error.HTTPError as e:
            msg = e.read()[:200].decode("utf-8", "replace")
            print(f"  HTTP {e.code}: {msg}", file=sys.stderr)
            if e.code in (401, 402, 403):
                sys.exit("Fish Audio refused the request (check the key / quota)")
        except Exception as e:  # noqa: BLE001
            print(f"  {type(e).__name__}: {e}", file=sys.stderr)
        time.sleep(2 + 3 * k)
    sys.exit("Fish Audio request kept failing")


def main():
    key = os.environ.get("FISH_API_KEY", "").strip()
    if not key:
        sys.exit("set FISH_API_KEY in the environment first")
    tmp = tempfile.mkdtemp(prefix="sneeze_voice_")
    parts = []
    for i, (a, b) in enumerate(BEATS):
        text = " ".join(speakable(x) for x in LINES[a:b])
        p = os.path.join(tmp, f"beat{i:02d}.mp3")
        print(f"beat {i + 1}/{len(BEATS)}: {text[:70]}...", flush=True)
        synth(text, p, key)
        parts.append(p)
    gap = os.path.join(tmp, "gap.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(GAP), gap],
                   check=True)
    lst = os.path.join(tmp, "list.txt")
    with open(lst, "w") as f:
        for i, p in enumerate(parts):
            f.write(f"file '{p}'\n")
            if i < len(parts) - 1:
                f.write(f"file '{gap}'\n")
    out = os.path.join(HERE, "sneeze_voiceover.mp3")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-ar", "44100", "-ac", "1",
                    "-c:a", "libmp3lame", "-b:a", "128k", out], check=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
