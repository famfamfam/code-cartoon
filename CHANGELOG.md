# Changelog

## 1.2.0 — 2026-10-17

Lessons from a real song: a 2.5-minute instrumental clip (a WWII dogfight in coloured-pencil 3D).

- **Pencil 3D (`engine/pencil3d.js`, loaded by the 2D template):** meshes (bodies, airfoil wings,
  plates, struts) seen through a camera and drawn in coloured pencil — sunlit fills, hatching and
  cross-hatching in the shade, boiling outlines along silhouettes and creases, part by part so a near
  part covers a far one; insignia and damage-only decals; cumulus clouds from flattened bumpy puffs that
  fade when the camera flies through; `P3.flight` (bank from the sideways acceleration, never flips) and
  `P3.track` (a path from a flight simulation run once at load). Guide: `references/pencil3d.md`.
- **Reading the music:** `cartoon song` prints a table per part — key, loudness, brightness, bass,
  note density, dynamics, stereo width, in words relative to the song. SKILL.md step 0 for clips: say
  honestly that Claude cannot hear the song, give a short reading from the numbers, then ask the genre,
  the lead instrument, the story and the ending.
- **Staged review for long videos:** keyframes, then a draft of each part (`cartoon cut <part> --from
  --to --size`), then the full render; every version the user saw is kept beside the new one.
- **Cuts without jerks** (SKILL.md rule 9). `P3.flight` stops its time window where a path jumps (a plane
  no longer comes into a new shot sideways), `P3.lag` for chase cameras that do not swing, `world.keep`
  so a cloud never hides the planes.
  - `cartoon frames --jumps`:
    - a cut explains one changed frame; a burst of changes after it is reported;
    - events with a `dur` (flashes) are planned all along;
    - the baseline is the median of the frames that changed, so camera moves in 3D on twos are not flagged.
  - `cartoon frames --around` shows every drawing next to each cut.
  - A frozen frame is explained as an exception (`cartoon check-hf`).
- Palette `sky` (sunny sky with dramatic clouds); `storm`, `dusk` and `sky` have `red`, `black`, `white`
  for insignia; `assets/themes.jpg` shows all 16 palettes (`cartoon palettes` lays them out in a square
  grid). 21 new pitfalls (3D attitude, aiming, trails across cuts, clouds, palette before
  geometry, cameras and cuts), a recipe "a duel in the sky", instrumentals and your own parts in `song-clip.md`.

## 1.1.0 — 2026-10-16

Clips to a song.

- **`cartoon song`:** the parts of a song (intro, verse, chorus, bridge, outro) from the tags of the
  lyrics as Suno/Udio write them, placed on the bars where the texture changes and where the voice sings;
  without lyrics, from the music alone. Every lyric line timed from the vocal stem, an LRC file (enhanced
  word times too) or spread on the bars. Writes `audio/song.lrc` (edit it to fix the timing), `song.srt`,
  `song.map.png` and `lyrics-preview.mp4` — the song with karaoke lines to check the timing in seconds,
  before any rendering. Pure numpy/scipy.
- **Template `clip`** (`cartoon new --template clip --song ... --lyrics ... --vocals ...`): the length
  comes from the song; a starter with one world per part — a pencil landscape drawn bar by bar, a neon
  sun in the chorus that grows with every repeat, a night with a star per beat, a poster on the outro.
- **`cartoon cut`:** a cut of the clip (the chorus for Reels, any format) as a generated project in
  `cuts/<name>/`, on bar lines, with its own poster; the audio fades in 20 ms and out 1.5 s.
- **Engine 1.2:** `Sketch.songScenes`, `d.beat`, `d.pulse()`, `d.energy`, `d.sec`, `d.lyric()` +
  `Sketch.fx.lyric` (write / karaoke / stamp / ribbon), `Sketch.safe()`, `Sketch.cam.kick`, `d.cue()` of
  a part, beatLock (on twos a new drawing starts on every beat), cues `window` for cuts. An iris no longer
  lets the old world's glow shine through the new one. Scenes without a song render as before.
- **Your own parts** for instrumentals or when the found parts are wrong: `cartoon song --parts
  "intro:0,fight:41.8,storm:1:23.1,outro:138.3"` (any labels, kept for later runs); music that changes
  every phrase is segmented per 4-bar phrase instead of per bar. New palettes `storm` and `dusk`.
- **Example `song-clip`** on a synthesized demo song (no third-party audio); `cartoon frames --jumps`
  knows part changes and lyric lines; `cartoon doctor` checks libass; `cartoon selfcheck` tests the song
  analysis against the demo song's known answers.

## 1.0.0 — 2026-10-16

First public release.

- **Engine 1.1 (2D):** several worlds in one video (`Sketch.sequence`: one palette, paper and camera
  per scene; iris and flash transitions), keyframed cameras (`Sketch.cam.keys`, `anchor`), line widths
  that follow the camera zoom, palette-pinned caches, captions from cues, crayon / marker / flat pens,
  lubok ornament frame and ribbon. Old scenes render pixel-identically.
- **Styles:** `crayon` (a child's drawing), `lubok` (Bilibin print), `cosmos` (photo + 3D); Ruslan
  Display and Lora fonts.
- **Templates:** the starter scene lays itself out for 9:16, 16:9, 1:1 and 4:5; a new `photo3d`
  template with `kit3d.js` (a pop-up book from any picture, a space kit, a face on a ball, falling
  leaves, Ken Burns on a real photo).
- **Sound:** music moods (`musicbox`, `folk`, `space`), new effects (`page`, `rumble`, `magic`,
  `wind`), your own tracks with ducking, narration with Piper / the system voice / your recordings
  (`cartoon voice --fit`), beat tracking and snapping (`cartoon beats`).
- **QA:** `cartoon frames` (zoomed crops, twitch and jump detector), `cartoon share` (light MP4, GIF,
  WebP), `cartoon doctor`, `cartoon selfcheck`.
- **Packaging:** one entry point `cartoon` (a real Python on every OS, pinned HyperFrames, UTF-8), a
  Claude Code plugin and marketplace, `claude plugin eval` cases, CI, English instructions and
  references, bundled examples (`cartoon example`).
