#!/usr/bin/env python3
"""Look closer at a render than a contact sheet can: zoomed crops, a twitch detector, jump finder.

  frame_check.py out.mp4 --zoom X,Y,W,H --at 20.9,21.0,21.1 [--scale 2] [-o zoom.jpg]
  frame_check.py out.mp4 --twitch X,Y,W,H --from 20 --to 24 [--k 5]
  frame_check.py out.mp4 --jumps [--cues cues.js] [--k 6] [-o jumps.jpg]
  (or: cartoon frames ...)

Coordinates are video pixels (x, y of the top-left corner, width, height).
--zoom    crops a region at several times and lays them out big, side by side. Use it for faces,
          eyes, small text — anything a 12-frame sheet shrinks to a few pixels.
--twitch  a region that should hold still (a face, a logo) is compared with its own temporal
          median; frames that differ far more than the usual line boil are listed. Catches a pupil
          that jumps, a sprite that gets clipped, a texture that flickers.
--jumps   whole-frame changes that are much bigger than their neighbours and do NOT sit on a cue
          time (cues.js events, parts of the song and lyric lines, ±0.15 s) — unplanned pops and flashes.
Needs ffmpeg, numpy, Pillow.
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

import numpy as np


def probe(v):
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                        "-show_entries", "format=duration", "-of", "json", str(v)], capture_output=True, text=True)
    j = json.loads(p.stdout)
    s = j["streams"][0]
    n, d = s["r_frame_rate"].split("/")
    return int(s["width"]), int(s["height"]), int(n) / int(d), float(j["format"]["duration"])


def gray_frames(v, t0=None, t1=None, crop=None, width=None):
    W, H, fps, dur = probe(v)
    vf = []
    if crop:
        x, y, w, h = crop
        vf.append(f"crop={w}:{h}:{x}:{y}")
        ow, oh = w, h
    else:
        ow, oh = W, H
    if width and ow > width:
        oh = int(round(oh * width / ow / 2) * 2)
        ow = width
        vf.append(f"scale={ow}:{oh}")
    vf.append("format=gray")
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error"]
    if t0 is not None:
        cmd += ["-ss", f"{t0:.3f}"]
    cmd += ["-i", str(v)]
    if t1 is not None:
        cmd += ["-t", f"{max(0.05, t1 - (t0 or 0)):.3f}"]
    cmd += ["-vf", ",".join(vf), "-f", "rawvideo", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(-1, oh, ow).astype(np.float32)
    times = (t0 or 0) + np.arange(len(f)) / fps
    return f, times, fps


def frame_at(v, t):
    from PIL import Image
    import io
    p = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(v), "-frames:v", "1",
                        "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
    return Image.open(io.BytesIO(p.stdout)).convert("RGB")


def robust_flags(x, k):
    med = np.median(x)
    mad = np.median(np.abs(x - med)) * 1.4826 + 1e-6
    return (x > med + k * mad) & (x > med * 1.8 + 0.5), med


def cue_times(path):
    if not path:
        return np.array([])
    txt = Path(path).read_text(encoding="utf-8")
    m = re.search(r"/\*JSON-START\*/(.*)/\*JSON-END\*/", txt, re.S)
    cues = json.loads(m.group(1))
    ev = cues["events"]
    ts = [e["t"] for e in ev if e.get("type") != "lyric"] + [e["t"] + e.get("dur", 0) for e in ev if e.get("dur") and e.get("type") != "lyric"]
    song = cues.get("song") or {}
    two = 120.0 / float(song.get("bpm") or 120)  # a transition between parts lasts up to two beats
    for s in song.get("sections", []):  # a new part of the song changes the picture for a while
        ts += list(np.arange(s["t"], s["t"] + two + 0.1, 0.1))
    ts += [e["t"] for e in ev if e.get("type") == "lyric"]  # a lyric line appears
    return np.array(ts) - float((cues.get("window") or {}).get("from", 0))  # a cut: song time -> video time


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--zoom", help="X,Y,W,H region to enlarge")
    ap.add_argument("--at", help="comma-separated times for --zoom")
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--twitch", help="X,Y,W,H region that should hold still")
    ap.add_argument("--from", dest="t0", type=float, default=None)
    ap.add_argument("--to", dest="t1", type=float, default=None)
    ap.add_argument("--jumps", action="store_true")
    ap.add_argument("--cues", help="cues.js: expected event times are not reported as jumps")
    ap.add_argument("--k", type=float, default=None, help="sensitivity (lower = more flags)")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    v = Path(a.video)
    if not v.exists():
        sys.exit(f"no such file: {v}")
    rc = 0

    if a.zoom:
        from PIL import Image, ImageDraw
        x, y, w, h = [int(float(s)) for s in a.zoom.split(",")]
        ts = [float(s) for s in (a.at or "0").split(",")]
        tiles = [frame_at(v, t).crop((x, y, x + w, y + h)).resize((int(w * a.scale), int(h * a.scale)), Image.LANCZOS) for t in ts]
        cols = min(len(tiles), max(1, int(2400 // tiles[0].width)))
        rows = (len(tiles) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tiles[0].width, rows * (tiles[0].height + 22)), (24, 24, 24))
        dr = ImageDraw.Draw(sheet)
        for i, (t, im) in enumerate(zip(ts, tiles)):
            cx, cy = (i % cols) * im.width, (i // cols) * (im.height + 22)
            sheet.paste(im, (cx, cy + 22))
            dr.text((cx + 6, cy + 4), f"{t:.2f}s  [{x},{y} {w}x{h}]", fill=(230, 230, 230))
        out = a.out or str(v.with_suffix("")) + ".zoom.jpg"
        sheet.save(out, quality=90)
        print(f"zoom grid: {out}  ({len(ts)} crops x{a.scale:g}) — open it and look")

    if a.twitch:
        x, y, w, h = [int(float(s)) for s in a.twitch.split(",")]
        f, ts, fps = gray_frames(v, a.t0, a.t1, crop=(x, y, w, h), width=480)
        if len(f) < 4:
            sys.exit("too few frames in the range")
        med = np.median(f, axis=0)
        dev = np.mean(np.abs(f - med), axis=(1, 2))
        flags, base = robust_flags(dev, a.k or 5.0)
        print(f"twitch check [{x},{y} {w}x{h}] {ts[0]:.2f}-{ts[-1]:.2f}s: {len(f)} frames, usual change {base:.2f}/255")
        hits = ts[flags]
        if len(hits):
            rc = 1
            print(f"  ! {len(hits)} frame(s) change much more than the usual boil:")
            for t, d in zip(hits, dev[flags]):
                print(f"    {t:7.3f}s  {d:.2f}/255")
            print(f"  look: cartoon frames {v.name} --zoom {x},{y},{w},{h} --at " + ",".join(f"{t:.2f}" for t in hits[:8]))
        else:
            print("  ok: nothing jumps beyond the line boil")

    if a.jumps:
        f, ts, fps = gray_frames(v, a.t0, a.t1, width=320)
        d = np.concatenate([[0], np.mean(np.abs(np.diff(f, axis=0)), axis=(1, 2))])
        win = max(3, int(fps))
        pad = np.pad(d, win, mode="edge")
        local = np.array([np.median(pad[i:i + 2 * win + 1]) for i in range(len(d))])
        k = a.k or 6.0
        flags = (d > local * k) & (d > 3.0)
        ct = cue_times(a.cues)
        expected = np.array([len(ct) > 0 and np.min(np.abs(ct - t)) <= 0.15 for t in ts])
        bad = flags & ~expected
        print(f"jump check: {len(f)} frames; {int(flags.sum())} big changes, {int((flags & expected).sum())} on cues, {int(bad.sum())} unexpected")
        for t, dd in zip(ts[bad], d[bad]):
            print(f"  ! {t:7.3f}s  change {dd:.1f}/255 (neighbours {np.median(d):.1f}) — not on any cue")
        if bad.any():
            rc = 1
            if a.out:
                from PIL import Image
                ims = []
                for t in ts[bad][:6]:
                    pair = [frame_at(v, max(0, t - 1 / fps)), frame_at(v, t)]
                    ims.append(pair)
                tw = 480
                th = int(ims[0][0].height * tw / ims[0][0].width)
                sheet = Image.new("RGB", (tw * 2, th * len(ims)), (0, 0, 0))
                for r, (p0, p1) in enumerate(ims):
                    sheet.paste(p0.resize((tw, th)), (0, r * th))
                    sheet.paste(p1.resize((tw, th)), (tw, r * th))
                sheet.save(a.out, quality=88)
                print(f"  before/after pairs: {a.out}")
        else:
            print("  ok: every big change sits on a cue")

    if not (a.zoom or a.twitch or a.jumps):
        ap.print_help()
    sys.exit(rc)


if __name__ == "__main__":
    main()
