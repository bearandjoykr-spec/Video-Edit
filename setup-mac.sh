#!/bin/bash
# One-command setup for The Bear & Joy Co. video editor on a Mac.
#
#   curl -fsSL https://raw.githubusercontent.com/bearandjoykr-spec/Video-Edit/claude/video-tools-setup/setup-mac.sh | bash
#   (or, inside an existing clone:  bash setup-mac.sh)
#
# Safe to run again: every step skips what is already done.
# What it does:
#   1. Clones (or updates) the project into ~/Video-Edit
#   2. Installs ffmpeg, cmake and Node with Homebrew if missing
#   3. Installs Remotion + HyperFrames (npm) and Python tools in a private venv
#   4. Downloads the brand fonts and builds Whisper (whisper.cpp) with its model
#   5. Adds a short note to ~/.claude/CLAUDE.md so every Claude session on this Mac,
#      in any folder, knows where the project lives and to read its brand rules first
set -euo pipefail

REPO_URL="https://github.com/bearandjoykr-spec/Video-Edit.git"
BRANCH="claude/video-tools-setup"
DIR="${VIDEO_EDIT_DIR:-$HOME/Video-Edit}"
say() { printf '\n\033[1m▶ %s\033[0m\n' "$*"; }

# 1. Project --------------------------------------------------------------------
say "Project folder: $DIR"
if [ -d "$DIR/.git" ]; then
  git -C "$DIR" fetch origin "$BRANCH"
  git -C "$DIR" checkout "$BRANCH"
  git -C "$DIR" pull --ff-only origin "$BRANCH" || echo "  (local changes present — left as they are; pull manually when ready)"
elif [ -d "$DIR" ] && [ -n "$(ls -A "$DIR" 2>/dev/null)" ]; then
  # A non-empty folder that is not the repo: never overwrite it. Put the repo next to it instead.
  echo "  $DIR already exists and is not the project repo. Its contents:"
  ls -la "$DIR" | head -20
  echo "  Leaving it untouched. Cloning the project into $DIR/project instead."
  DIR="$DIR/project"
  [ -d "$DIR/.git" ] && git -C "$DIR" pull --ff-only origin "$BRANCH" || git clone --branch "$BRANCH" "$REPO_URL" "$DIR"
else
  git clone --branch "$BRANCH" "$REPO_URL" "$DIR"
fi
cd "$DIR"

# 2. System tools -----------------------------------------------------------------
say "System tools"
if ! command -v brew >/dev/null 2>&1; then
  echo "  Homebrew is not installed. Install it from https://brew.sh, then run this script again."
  exit 1
fi
for pkg in ffmpeg cmake node; do
  if brew list --formula "$pkg" >/dev/null 2>&1 || command -v "$pkg" >/dev/null 2>&1; then
    echo "  $pkg: ok"
  else
    brew install "$pkg"
  fi
done

# 3. Project dependencies -----------------------------------------------------------
say "Remotion + HyperFrames"
npm ci --prefix remotion

say "Python tools (private venv in .venv)"
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip numpy yt-dlp pillow

# 4. Fonts and Whisper ----------------------------------------------------------------
say "Brand fonts"
sh remotion/fetch-fonts.sh >/dev/null && echo "  fonts: ok"

say "Whisper (whisper.cpp)"
W="$DIR/tools/whisper.cpp"
[ -d "$W/.git" ] || git clone --depth 1 https://github.com/ggml-org/whisper.cpp "$W"
if [ ! -x "$W/build/bin/whisper-cli" ]; then
  (cd "$W" && cmake -B build -DCMAKE_BUILD_TYPE=Release >/dev/null && cmake --build build -j --config Release --target whisper-cli)
fi
[ -f "$W/models/ggml-large-v3-turbo.bin" ] || (cd "$W" && sh ./models/download-ggml-model.sh large-v3-turbo)
echo "  whisper: $W/build/bin/whisper-cli"

# 5. Global pointer for every Claude session on this Mac ---------------------------------
say "Claude note in ~/.claude/CLAUDE.md"
mkdir -p "$HOME/.claude"
G="$HOME/.claude/CLAUDE.md"
MARK="<!-- bear-and-joy-video-edit -->"
if grep -q "$MARK" "$G" 2>/dev/null; then
  echo "  already present"
else
  cat >> "$G" <<EOF

$MARK
## The Bear & Joy Co. — video editing
For any video, reel or Instagram editing for The Bear & Joy Co., work inside \`$DIR\`
(git repo bearandjoykr-spec/Video-Edit, branch $BRANCH), even if this session started elsewhere.
1. \`git pull\` there first, then read \`$DIR/CLAUDE.md\` and \`$DIR/brand/BRAND.md\` before doing anything.
2. Raw footage can stay where it is (e.g. ~/Downloads); copy or link it into \`$DIR/raw-footage/\`.
3. When done, commit and push, so cloud sessions and this Mac stay in sync.
Other Claude threads cannot be read from here; the repo is the shared memory.
EOF
  echo "  added"
fi

say "Done. Open Claude Code in $DIR for video work."
