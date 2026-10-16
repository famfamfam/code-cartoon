# Contributing

Thanks for helping. Issues and pull requests are welcome in English or Russian.

## Set up
```bash
git clone https://github.com/famfamfam/code-cartoon && cd code-cartoon
skills/code-cartoon/scripts/cartoon doctor
```
To use your working copy as your installed skill, link the skill folder into Claude Code's skills
folder: `ln -s "$PWD/skills/code-cartoon" ~/.claude/skills/code-cartoon` (on Windows:
`mklink /J %USERPROFILE%\.claude\skills\code-cartoon <repo>\skills\code-cartoon`). Link
`skills/code-cartoon`, not the repository root: a folder with `.claude-plugin/` inside
`~/.claude/skills` loads as a plugin with a namespaced command.

## Before a pull request
```bash
skills/code-cartoon/scripts/cartoon selfcheck
claude plugin validate . --strict
```
If you changed the engine, render one example before and after
(`cartoon example lubok-sun-ship /tmp/x`) and compare the contact sheets. Old scenes must render the same.

## Rules of the code
- Everything that is drawn is a pure function of time; randomness only through seeded generators.
- Colours only through palette roles; a new role goes into every palette that needs it and into
  `scripts/selfcheck.py`.
- Text files use LF (`.gitattributes` enforces it); Python that writes files uses `newline="\n"`.
- Scripts run on Windows (Git Bash), macOS and Linux; go through `scripts/_lib.sh` for Python.

## Add a ...
- **Palette:** an object in `assets/template/engine/palettes.js` (strict JSON), then
  `cartoon palettes <project>`; every frame must still look right.
- **Style:** a DNA section in `references/styles.md` (6–10 rules, which pens and palette), ideally an
  example in `skills/code-cartoon/examples/<name>/` (`example.json` + the files that differ from the template).
- **Sound:** a `v_<name>` function and a line in the `gen` table of `scripts/synth_audio.py`, a row in
  `references/sound.md`, the type in the comment of `assets/template/cues.js`.
- **Pitfall:** one line "symptom | cause | fix" in `references/pitfalls.md`, in its section.
- **Eval:** a folder in `evals/` with `prompt.md` and `graders/` (see `docs/testing.md`).

## Commits
A short imperative subject, a body when the reason is not obvious. Commit as yourself; this project
lists only human authors.
