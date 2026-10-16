# Pitfalls

Add a line for every new mistake: symptom | cause | fix. One line, one pitfall. Read before writing
scenes. Grouped by area; numbers are stable ids (new ones go at the end of their section with the
next free number).

## Determinism and time
| # | symptom | cause | fix |
|---|---|---|---|
| 1 | stars/objects jump when neighbours appear | random numbers pulled from a shared stream inside a visibility check | key `Sketch.rng(id, i)` by object; with a shared stream draw ALL numbers first, then skip the invisible |
| 2 | randomness differs on every render | `Math.random`, `Date.now`, `performance.now` | only `Sketch.rng` / `noise1`; time only `d.t` |
| 8 | sound drifted from the picture | timing/length changed but the sound was not rebuilt | time lives only in `cues.js`; after a change run `cartoon audio` |
| 20 | an event after the end breaks the sound | `t` >= length | the script skips it with a warning; fix `cues.js` |
| 37 | "started earlier" with `Math.pow(u, 0.75)` but the drawing starts later | a power < 1 raises u in (0,1) -> later time | earlier = power > 1 (`u^1.3`); check the frame right after the start |
| 38 | a looped video (avatar, background) clicks at the seam | elements are not periodic: camera/particles/drawing at t=L differ from t=0 | everything periodic (`sin(2πn·t/P)`) or 0 at both ends; the next loop's drawing from `t − P`; compare the last and first frame side by side |
| 39 | in a loop the start of the next round is empty | "after the twist" fades are computed from `t`, not from the loop time `tc = t − P` | all drawing phases from `tc`; only once-per-loop things (photo, erase) from `t` |

## Drawing (2D engine)
| # | symptom | cause | fix |
|---|---|---|---|
| 3 | lines do not boil, the drawing is dead | `k` not passed to the pen | `{ k: d.k, seed: "unique" }` in every call |
| 4 | everything boils in sync | the same `seed` on different objects | a unique `seed` per object |
| 5 | a front object erased the back one too early | the "eraser" (destination-out / paper fill) runs before the object appears | gate it with `prog(t, appear, ...) > 0`; draw the back object first |
| 6 | hatching on light paper looks like a negative | the light is hatched instead of the shadow | `shade: light` -> hatch the shadow; `dark` -> the light (`d.pal.shade`) |
| 11 | a global flash washes the whole frame | the whole glow layer filled with bloom and `lighter` | a local radial flash (`fx.flash` with `radius`), alpha <= 0.35 for accents, <= 0.6 for transitions |
| 12 | rays/decor cross the object | directions not filtered | drop the angles where an element overlaps the object |
| 21 | text goes under the Reels interface | the bottom of the frame | keep the bottom 15 % empty; `cartoon sheet` marks the zone |
| 22 | rendering is very slow | screenshot mode without headless-shell, many hatch strokes, big blur | `npx hyperframes browser ensure`; sparser hatching; blur <= 26 px |
| 25 | a caption leaves by "un-writing" its letters | the text `progress` multiplied by the fade-out | appear with `progress`, leave with a separate `alpha`/scale of the whole plate (`fx.ribbon` `out`) |

## Several worlds and cameras
| # | symptom | cause | fix |
|---|---|---|---|
| 23 | a second world in another palette repaints wrong, or a cached picture changes colours | palettes switched by hand; a cache miss draws with the current world's palette | `Sketch.sequence` (one palette + paper per scene), `Sketch.withPalette`, `Sketch.cache(..., {palette})` pins the palette |
| 24 | at a big zoom pencil lines become thick ropes and dance | width and wobble scale with the camera | built in: `Sketch.config.zoomComp = 0.75` (per call `zoomComp:false`); use `d.useCamera` for worlds with their own camera so the zoom is known |
| 26 | a flying object passes over a standing one | paths not checked against other objects' places | check every stop/hover on the sheet; separate them by height or draw the far one first |

## Text and fonts
| # | symptom | cause | fix |
|---|---|---|---|
| 7 | hand-written letters break or double | an outline font traced as a line | write with `pen.text` (mask + reveal); "pen in the centre" needs a monoline font |
| 14 | canvas falls back to a system font | canvas draws before the font loads | the face in `fonts:` of `mount`; `@font-face` in `index.html` |
| 29 | a caption is unreadable over a glowing object | gold on gold, glow under the text | the caption in a calm area + a dark shadow `0 3px 12px rgba(0,0,0,.95)` |

## 3D and photo3d
| # | symptom | cause | fix |
|---|---|---|---|
| 15 | a 3D object does not fit a vertical frame | the FOV is vertical, the frame is narrow | camera distance from the width: `visH = max(width/aspect, height)` (in the template) |
| 16 | the 3D picture depends on the machine | DPR, `requestAnimationFrame`, particle simulation | `setPixelRatio(1)`, a fixed size, positions = f(t) |
| 28 | a flying rocket shows only its nozzle and a flare | the target is "into the depth", the camera behind | put targets to the side of the camera (motion across the view); check the frame in the middle of every flight |
| 30 | a portrait photo in 16:9 has bars or is soft | the frame is wider than the photo | `cartoon photo` scales it to cover the frame; move the camera vertically; the face no closer than 1.3x; ask for the original |
| 31 | 3D cut-outs (pop-up): alpha in the wrong place, square shadows | alphaMap reads the same UVs as map; the shadow ignores alpha | a mask over the WHOLE sheet; `customDepthMaterial = MeshDepthMaterial({alphaMap, alphaTest})` (`kit3d.popupCutouts`) |
| 32 | two WebGL canvases: reflections gone / errors | a PMREM environment texture belongs to its renderer | one `PMREMGenerator` per renderer (`kit3d.envMap`) |
| 33 | leaves/particles cross a face on the poster | random paths over the main object | hide elements whose paths cross the face/text area (`leavesOverlay.update(..., avoid)`) |
| 34 | a face sprite (a sun) has a wedge cut out of an eye | a sprite is screen-aligned: off-centre, its edge tilts into the ball | float it 1.7 R in front and rescale `s·(d−off)/(d−R)`; clip the pupils to the eye white (`kit3d.faceSprite`) |
| 35 | a character's eyes twitch | the gaze is quantised and follows the target's bob | gaze = a smooth function of the path without the bob, no rounding; redraw the face every frame |
| 36 | a 3D planet looks like a glass ball | low ocean roughness + strong environment + a bright rim | ocean roughness >= 0.5, `envMapIntensity` 0.1–0.15, fresnel power >= 3, rim <= 0.9 |
| 41 | `Object.assign(mesh, { position })` throws in a module | Object3D `position` is read-only | `mesh.position.copy(v)` |
| 42 | fresnel shader: black blotches on some GPUs (lint `shader_unbounded_cosine_pow`) | `pow(1 - max(dot,0), k)` can get a negative base | `pow(1.0 - clamp(dot(n, v), 0.0, 1.0), k)` |

## Sound
| # | symptom | cause | fix |
|---|---|---|---|
| 9 | the render is silent | `<audio>` has no `id`, or no `audio/mix.wav` | an `id` + run `cartoon audio` |
| 19 | loudness jumps from video to video | normalised by peak | `cartoon audio` normalises by LUFS (−15) + limiter |

## Rotoscope
| # | symptom | cause | fix |
|---|---|---|---|
| 17 | the whole background is hatched | a dark background falls into the "darkest 30 %" | `--shadow 0` or a light background in the source |
| 18 | lines are noisy dots | XDoG threshold too low / small details | `--threshold 0.18`, `--detail 1.3` |

## Platform (Windows, shells)
| # | symptom | cause | fix |
|---|---|---|---|
| 13 | lint: `missing_timeline_registry` | the timeline is registered only in an external js | an inline script with `window.__timelines` in `index.html` (in the templates) |
| 27 | Cyrillic looks like mojibake in python/sed output on Windows | the console is cp1251, the file is fine (UTF-8) | check bytes with `od -c` / grep the file; do not "repair" it; `cartoon` sets `PYTHONIOENCODING=utf-8` |
| 40 | `analyze_reference.py` fails with `UnicodeEncodeError` on Windows | cp1251 console, Cyrillic in the report | run through `cartoon` (UTF-8) or set `PYTHONIOENCODING=utf-8` |
| 43 | args from a Python helper arrive as `--template\r` in bash | Python on Windows prints CRLF; `"${x%$'\r'}"` inside double quotes does not strip it | `CR=$(printf '\r'); x=${x%"$CR"}` or `tr -d '\r'` |
| 44 | files written by a Python snippet get CRLF | text mode on Windows converts `\n` | `open(p, "w", encoding="utf-8", newline="\n")`; `.gitattributes` keeps LF in the repo |
| 45 | a Python subprocess runs "bash" and gets WSL ("execvpe(/bin/bash) failed") | `C:\Windows\System32\bash.exe` comes first on PATH | use the bash that runs us: `CARTOON_BASH` (exported by `cartoon`) |
| 46 | `node --check` fails on ES modules (`import`) | `.js` is CommonJS for node | check a `.mjs` copy (`cartoon selfcheck` does it) |
