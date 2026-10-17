# Testing

## Automatic
- `skills/code-cartoon/scripts/cartoon selfcheck` — palettes and roles, template timings, fonts and
  licences, JS syntax, privacy scan, beat tracker on a 120 BPM click track, Suno lyrics and LRC parsing,
  the song analysis on a synthesized demo song with known answers (parts on the right bars with the vocal
  stem, without it, from an LRC and from the music alone; line starts within a beat / a bar), a fresh
  project's soundtrack.
- `claude plugin validate . --strict` — the plugin and marketplace manifests.
- CI (`.github/workflows/ci.yml`) runs both, shellcheck and Python syntax checks, and renders the 2d, 3d
  and photo3d starters for 3 s on Ubuntu (`cartoon check` + `cartoon frames --jumps`), builds the
  `song-clip` example and renders a 9:16 cut of its chorus. On Windows it builds a project and its
  soundtrack.

## Skill behaviour (`claude plugin eval`)
`evals/` holds cases for `claude plugin eval .`: the skill must start on Russian and English requests
for a cartoon and on "bring my drawing to life", ask questions before writing code, and stay away from
neural video generation and slide decks. Every run is a real model call on your account:
```bash
claude plugin eval . --runs 1            # quick
claude plugin eval . --tag trigger       # only the trigger cases
```

## End to end (by hand, before a release)
Run each prompt in a fresh session with the skill installed; answer "STOP — decide yourself" to the
first batch of questions unless the prompt says otherwise.

| Case | Prompt | Must hold |
|---|---|---|
| pencil reel | A 10-second 9:16 pencil reel: a seed grows into a tree, the caption "Grow every day" | questions with a STOP option before code; storyboard in `project.md` before the scene; `cartoon check` passes (10 s, 24 fps, 1080x1920, sound); "on TWOS" in `cartoon analyze out.mp4`; the first frame is not empty; the twist at 35–45 %; no `Math.random`/`Date.now`; colours only by role; no text in the bottom 15 % |
| recolour | Recolour it in blueprint and render again (after the reel) | only the `PALETTE` line changes; no colour of the old palette survives |
| references | Here are 3 reference videos; make 12 s 9:16 about our delivery service | `cartoon analyze` on all three, 6–10 rules with numbers, no copied frames, a palette added as roles |
| glass intro | A 6 s 16:9 intro: glass and chrome, particles snap into a ring, title "AI WEEK" | `--template 3d`; hero not cropped; particles = f(t) |
| rotoscope | Here is a video of me waving (refs/wave.mp4), make it chalk with "Hi!" | `cartoon roto` at 12 fps; lines boil; chalk palette; readable caption |
| two worlds | A pencil sketch of a boat that turns into a lubok print | `Sketch.sequence` with an iris; the lubok frame and ribbon draw on |
| photo + 3D | My child's drawing (refs/drawing.jpg) and photo (refs/kid.jpg): a fairy tale where the child flies into the drawing | `--template photo3d`; ellipses around the drawing's objects; the photo never leaves the folder; `cartoon frames --twitch` on the faces |
| narration | add a narrator to any of the above | `cartoon voice --fit`; ducking reported by `cartoon audio`; captions match the speech |
| song | Cut it to audio/song.mp3 | `cartoon beats --snap`; the song in `tracks`; the twist on the drop |
| song clip | Make a clip to my Suno song (song.mp3, lyrics.txt with tags, vocals.wav), 16:9, and the chorus for Reels | asks for the lyrics/stem/formats first; `--template clip`; `song.map.png` parts match the tags; the user is asked to watch `lyrics-preview.mp4` (or told the timing was checked on the map only); a storyboard by parts; the chorus grows; `cartoon cut reel --auto --format 9:16`; lyrics never in the bottom 15 % of the cut; `cartoon check` length = the song / the cut |
| no trigger | Generate a video of my cat with Sora | the skill is not used |
