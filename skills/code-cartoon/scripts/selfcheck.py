#!/usr/bin/env python3
"""Self-check of the skill itself (run before a release and in CI).   cartoon selfcheck [--quick]

  palettes   strict JSON; every palette has the base roles; crayon/lubok/cosmos have their extra roles
  templates  cues.js blocks parse; ids unique; every event type is known to synth_audio.py
  fonts      every @font-face file exists; every font family ships its licence
  vendor     three.js / GSAP present with their licence notes
  js         node --check on the engine, scenes and modules
  privacy    no absolute user paths or e-mail addresses in text files
  beats      a synthetic 120 BPM click track -> 120 +- 1 BPM, beats within 30 ms
  audio      a fresh project builds its soundtrack at -15 +- 1 LUFS (skipped with --quick)
Exit code 0 = all good.
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile, wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))
fails, notes = [], []


def check(name, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}{('  ' + detail) if detail else ''}")
    if not ok:
        fails.append(name)


def block(path, placeholders=None):
    txt = Path(path).read_text(encoding="utf-8")
    for k, v in (placeholders or {}).items():
        txt = txt.replace(k, v)
    m = re.search(r"/\*JSON-START\*/(.*)/\*JSON-END\*/", txt, re.S)
    return json.loads(m.group(1))


BASE = ["paper", "tooth", "line", "soft", "guide", "a1", "a2", "a3", "warm", "glow", "shade", "kind"]
CRAYON = ["sheet", "navy", "violet", "sun", "orange", "red", "sky", "green", "grey", "black", "brown", "hair", "skin", "cheek"]
COSMOS = CRAYON + ["metal", "gold", "wood", "woodgap", "ocean", "space", "nebula1", "nebula2", "leaf1", "leaf2", "leaf3"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quick", action="store_true", help="skip the audio build")
    a = ap.parse_args()
    print(f"code-cartoon selfcheck  ({SKILL})")

    # palettes
    try:
        pal = block(SKILL / "assets/template/engine/palettes.js")
        missing = {n: [r for r in BASE if r not in p] for n, p in pal.items()}
        missing = {n: m for n, m in missing.items() if m}
        check(f"palettes: {len(pal)} parse, base roles", not missing, str(missing) if missing else "")
        for name, roles in (("crayon", CRAYON), ("lubok", CRAYON), ("cosmos", COSMOS)):
            lack = [r for r in roles if r not in pal.get(name, {})]
            check(f"palette {name}: extra roles", not lack, ", ".join(lack))
    except Exception as e:  # noqa: BLE001
        check("palettes.js parses", False, str(e))

    # templates: cues
    import synth_audio
    known = set(re.findall(r'"([a-z]+)": lambda', (HERE / "synth_audio.py").read_text(encoding="utf-8"))) | {"none", "voice", "caption"}
    for t in ("template", "template-photo3d"):
        try:
            c = block(SKILL / f"assets/{t}/cues.js", {"__DUR__": "10"})
            ids = [e["id"] for e in c["events"]]
            check(f"{t}/cues.js parses, ids unique", len(ids) == len(set(ids)))
            unknown = sorted({e.get("type", "none") for e in c["events"]} - known)
            check(f"{t}/cues.js event types known", not unknown, ", ".join(unknown))
            if c.get("music", {}).get("mood"):
                check(f"{t}/cues.js music mood exists", c["music"]["mood"] in synth_audio.MOODS, c["music"]["mood"])
        except Exception as e:  # noqa: BLE001
            check(f"{t}/cues.js parses", False, str(e))

    # fonts + licences
    for t in ("template", "template-3d", "template-photo3d"):
        html = SKILL / f"assets/{t}/index.html"
        urls = re.findall(r'url\("(fonts/[^"]+)"\)', html.read_text(encoding="utf-8"))
        lost = [u for u in urls if not ((SKILL / f"assets/{t}" / u).exists() or (SKILL / "assets/template" / u).exists())]
        check(f"{t}: {len(urls)} font files present", not lost, ", ".join(lost))
    lic = {"caveat": "LICENSE-Caveat-OFL.txt", "inter": "LICENSE-Inter-OFL.txt", "ruslan": "LICENSE-RuslanDisplay-OFL.txt"}
    for fam, f in lic.items():
        check(f"font licence {f}", (SKILL / "assets/template/fonts" / f).exists())
    check("font licence LICENSE-Lora-OFL.txt", (SKILL / "assets/template-photo3d/fonts/LICENSE-Lora-OFL.txt").exists())
    check("vendor: three.js + MIT note", (SKILL / "assets/template-3d/vendor/three.module.min.js").exists() and (SKILL / "assets/template-3d/vendor/LICENSE-three-MIT.txt").exists())
    g = SKILL / "assets/template/vendor/gsap.min.js"
    check("vendor: GSAP with its notice header", g.exists() and "standard-license" in g.read_text(encoding="utf-8", errors="ignore")[:600])
    check("sample photo licence record", (SKILL / "assets/template-photo3d/assets/sample-photo.LICENSE.json").exists())

    # js syntax
    node = shutil.which("node")
    if node:
        js = [SKILL / "assets/template/engine/sketch.js", SKILL / "assets/template/engine/palettes.js", SKILL / "assets/template/scene.js", SKILL / "assets/template/cues.js"]
        bad = [p.name for p in js if subprocess.run([node, "--check", str(p)], capture_output=True).returncode != 0]
        mods = [SKILL / "assets/template-3d/scene3d.js", SKILL / "assets/template-photo3d/scene3d.js", SKILL / "assets/template-photo3d/kit3d.js"]
        with tempfile.TemporaryDirectory() as td:  # ES modules: check a .mjs copy
            for p in mods:
                q = Path(td) / (p.parent.name + "-" + p.stem + ".mjs")
                q.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
                if subprocess.run([node, "--check", str(q)], capture_output=True).returncode != 0:
                    bad.append(p.parent.name + "/" + p.name)
        check("node --check (engine, scenes, modules)", not bad, ", ".join(bad))
    else:
        notes.append("node not found: JS syntax not checked")

    # privacy
    pat = re.compile(r"([A-Za-z]:[\\/]Users[\\/]|/Users/[a-z]|/home/[a-z]|[\w.+-]+@[\w-]+\.[\w.]+)")
    hits = []
    for p in SKILL.rglob("*"):
        if p.is_file() and p.suffix in {".md", ".sh", ".py", ".js", ".json", ".html", ".txt"} and "vendor" not in p.parts and p.name != "selfcheck.py":
            for m in pat.finditer(p.read_text(encoding="utf-8", errors="ignore")):
                s = m.group(0)
                if not re.search(r"(noreply|example\.com|users\.noreply|@anthropic-ai|@fontsource|@\d|greensock\.com)", s):
                    hits.append(f"{p.relative_to(SKILL)}: {s}")
    check("privacy: no user paths / e-mails", not hits, "; ".join(hits[:5]))

    # beats calibration
    try:
        import numpy as np
        import beats
        with tempfile.TemporaryDirectory() as td:
            sr, bpm, t0 = 44100, 120.0, 0.5
            x = np.zeros(int(20 * sr)); truth = []
            for k in range(int((20 - t0) * bpm / 60)):
                t = t0 + k * 60 / bpm; truth.append(t); i = int(t * sr); n = int(0.05 * sr); tt = np.arange(n) / sr
                x[i:i + n] += (np.sin(2 * np.pi * (1500 if k % 4 else 80) * tt) * np.exp(-tt * (60 if k % 4 else 25)) * (0.5 if k % 4 else 0.9))[: len(x) - i]
            f = Path(td) / "click.wav"
            with wave.open(str(f), "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
            res, _ = beats.analyse(f)
            b = np.array(res["beats"]); truth = np.array(truth)
            err = np.array([b[np.argmin(np.abs(b - t))] - t for t in truth if b.min() - 0.1 < t < b.max() + 0.1])
            check("beats: 120 BPM click track", abs(res["bpm"] - 120) <= 1 and np.max(np.abs(err)) <= 0.03, f"{res['bpm']} BPM, max error {np.max(np.abs(err)) * 1000:.0f} ms")
    except Exception as e:  # noqa: BLE001
        check("beats: 120 BPM click track", False, str(e))

    # audio build in a fresh project
    if not a.quick:
        with tempfile.TemporaryDirectory() as td:
            proj = Path(td) / "p"
            sh = os.environ.get("CARTOON_BASH") or shutil.which("bash")  # on Windows PATH's bash may be WSL's
            r = subprocess.run([sh, str(HERE / "new_project.sh"), str(proj), "--duration", "4"], capture_output=True, text=True, encoding="utf-8", errors="replace")
            mm = re.search(r"integrated (-?[\d.]+) LUFS", r.stdout)
            ok = r.returncode == 0 and (proj / "audio/mix.wav").exists() and mm and abs(float(mm.group(1)) + 15) <= 1
            check("new project + soundtrack (-15 LUFS)", bool(ok), (mm.group(0) if mm else (r.stderr or r.stdout)[-200:]))

    for n in notes:
        print("  note  " + n)
    print("RESULT: " + ("pass" if not fails else f"FAIL ({len(fails)})"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
