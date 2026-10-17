# Changelog

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
