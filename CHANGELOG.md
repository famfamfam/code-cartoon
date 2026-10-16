# Changelog

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
