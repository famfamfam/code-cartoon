#!/usr/bin/env bash
# New code-cartoon project in one command.
#
#   new_project.sh <dir> [--format 9:16|16:9|1:1|4:5] [--duration 10] [--palette neon]
#                        [--size WxH] [--title "IDEA"] [--lang en] [--template 2d|3d|photo3d]
#                        [--photo person.jpg] [--image drawing.jpg]        (photo3d only)
#
# Copies the template (engine, fonts, vendored libs, starter scene, cues), fills size /
# duration / palette / title, scales the starter timing to the duration and builds the
# starter soundtrack. The starter works in every format.
set -euo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

usage="usage: new_project.sh <dir> [--format 9:16|16:9|1:1|4:5] [--size WxH] [--duration 10] [--palette neon] [--title TEXT] [--lang en] [--template 2d|3d|photo3d] [--photo FILE] [--image FILE]"
DIR="${1:-}"; [ -z "$DIR" ] && { echo "$usage"; exit 1; }
shift
FORMAT="9:16"; SIZE=""; DUR="10"; PALETTE=""; TITLE="IDEA"; TEMPLATE="2d"; LANG_="en"; PHOTO=""; IMAGE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --format) FORMAT="$2"; shift 2;;
    --size) SIZE="$2"; shift 2;;
    --duration) DUR="$2"; shift 2;;
    --palette) PALETTE="$2"; shift 2;;
    --title) TITLE="$2"; shift 2;;
    --template) TEMPLATE="$2"; shift 2;;
    --lang) LANG_="$2"; shift 2;;
    --photo) PHOTO="$2"; shift 2;;
    --image) IMAGE="$2"; shift 2;;
    *) echo "unknown option $1"; echo "$usage"; exit 1;;
  esac
done
[ "$TEMPLATE" = "sketch" ] && TEMPLATE="2d"
case "$TEMPLATE" in 2d|3d|photo3d) ;; *) echo "--template must be 2d, 3d or photo3d"; exit 1;; esac
[ -z "$PALETTE" ] && { [ "$TEMPLATE" = "photo3d" ] && PALETTE="cosmos" || PALETTE="neon"; }
case "$FORMAT" in
  9:16) W=1080; H=1920;;
  16:9) W=1920; H=1080;;
  1:1)  W=1080; H=1080;;
  4:5)  W=1080; H=1350;;
  *) echo "format must be 9:16, 16:9, 1:1 or 4:5"; exit 1;;
esac
[ -n "$SIZE" ] && { W="${SIZE%x*}"; H="${SIZE#*x}"; FORMAT="custom"; }
PALFILE="$SKILL_DIR/assets/template/engine/palettes.js"

if ! grep -q "\"$PALETTE\"" "$PALFILE"; then
  echo "unknown palette '$PALETTE'. Available:"; grep -oE '^  "[a-z0-9_-]+"' "$PALFILE" | tr -d ' "'; exit 1
fi
[ -e "$DIR" ] && [ -n "$(ls -A "$DIR" 2>/dev/null)" ] && { echo "$DIR exists and is not empty"; exit 1; }

mkdir -p "$DIR"
cp -R "$SKILL_DIR/assets/template/." "$DIR/"
case "$TEMPLATE" in
  3d)
    cp "$SKILL_DIR/assets/template-3d/index.html" "$SKILL_DIR/assets/template-3d/scene3d.js" "$DIR/"
    cp -R "$SKILL_DIR/assets/template-3d/vendor/." "$DIR/vendor/"
    rm -f "$DIR/scene.js";;
  photo3d)
    cp -R "$SKILL_DIR/assets/template-photo3d/." "$DIR/"
    cp -R "$SKILL_DIR/assets/template-3d/vendor/." "$DIR/vendor/"
    rm -f "$DIR/scene.js"
    need_python
    "$PY" "$SKILL_DIR/scripts/prep_photo.py" "$DIR" ${PHOTO:+--photo "$PHOTO"} ${IMAGE:+--image "$IMAGE"} --width "$W" --height "$H"
    rm -f "$DIR"/assets/sample-*;;
esac

esc() { printf '%s' "$1" | sed -e 's/[\/&|]/\\&/g'; }
for f in "$DIR/index.html" "$DIR/cues.js" "$DIR"/scene*.js; do
  [ -f "$f" ] || continue
  sed -i.bak -e "s|__W__|$W|g" -e "s|__H__|$H|g" -e "s|__DUR__|$DUR|g" -e "s|__LANG__|$(esc "$LANG_")|g" \
             -e "s|__PALETTE__|$(esc "$PALETTE")|g" -e "s|__TITLE__|$(esc "$TITLE")|g" "$f" && rm -f "$f.bak"
done

# the starter timing is written for 10 s (photo3d: 12 s); stretch it to the requested length
if [ -n "$PY" ]; then
  "$PY" - "$DIR/cues.js" "$DUR" "$TEMPLATE" "$SKILL_DIR/scripts" <<'PYEOF'
import sys
path, dur, template = sys.argv[1], float(sys.argv[2]), sys.argv[3]
sys.path.insert(0, sys.argv[4])
import _cues
base = 12.0 if template == "photo3d" else 10.0
if abs(dur - base) > 1e-6:
    cues = _cues.load(path)
    k = dur / base
    for e in cues["events"]:
        e["t"] = round(e["t"] * k, 3)
        if "dur" in e:
            e["dur"] = round(e["dur"] * k, 3)
    _cues.save(path, cues)
PYEOF
fi

cat > "$DIR/.gitignore" <<'EOF'
.hyperframes/
*.mp4
*.first.png
*.last.png
*.sheet.jpg
audio/voice/
EOF

cat > "$DIR/project.md" <<EOF
# $(basename "$DIR")
- format: $FORMAT (${W}x${H}), duration: ${DUR}s, palette: $PALETTE, template: $TEMPLATE, language: $LANG_
- render: 24 fps, drawings on twos (12/s)

## story

## storyboard (time / what is drawn / camera / sound)
| time | drawn | camera | sound |
|------|-------|--------|-------|
EOF

if [ -n "$PY" ] && "$PY" -c "import numpy, scipy" 2>/dev/null; then
  "$PY" "$SKILL_DIR/scripts/synth_audio.py" "$DIR" | tail -1
else
  echo "! Python with numpy/scipy not found: pip install numpy scipy pillow (then run: cartoon audio)"
fi
echo "created $DIR  (${W}x${H}, ${DUR}s, palette $PALETTE, template $TEMPLATE)"
echo "next: cd $DIR && $SKILL_DIR/scripts/cartoon lint && $SKILL_DIR/scripts/cartoon snapshot --at 0,3.9,6,9.5"
