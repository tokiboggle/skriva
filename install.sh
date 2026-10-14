#!/usr/bin/env bash
# skriva installer (macOS). Installs to ~/.skriva and a 'skriva' command in ~/.local/bin.
set -euo pipefail
DEST="${SKRIVA_HOME:-$HOME/.skriva}"; BIN="${SKRIVA_BIN:-$HOME/.local/bin}"
SRC="${SKRIVA_SRC:-https://raw.githubusercontent.com/tokiboggle/skriva/main/skriva.py}"
command -v ffmpeg >/dev/null || { echo "skriva needs ffmpeg: brew install ffmpeg"; exit 1; }
PY=""; for p in python3.13 python3.12 python3.11 python3.10; do command -v $p >/dev/null && { PY=$p; break; }; done
[ -z "$PY" ] && { echo "Need Python 3.10-3.13 (brew install python@3.13)"; exit 1; }
mkdir -p "$DEST" "$BIN"
"$PY" -m venv "$DEST/venv"
"$DEST/venv/bin/pip" install -q --upgrade pip
"$DEST/venv/bin/pip" install -q torch transformers numpy huggingface_hub
if [ -f "$SRC" ]; then cp "$SRC" "$DEST/skriva.py"; else curl -fsSL "$SRC" -o "$DEST/skriva.py"; fi
echo "Downloading the two Faroese models (~2.2 GB, one time)..."
HF_HOME="$DEST/hf" "$DEST/venv/bin/python" - <<'PY'
from huggingface_hub import snapshot_download as d
for r in ["carlosdanielhernandezmena/wav2vec2-large-xlsr-53-faroese-100h",
          "carlosdanielhernandezmena/whisper-small-faroese-5k-steps-100h"]:
    d(r, ignore_patterns=["training_args.bin", "*.msgpack", "*.h5", "*.ot"]); print("ok", r)
PY
cat > "$BIN/skriva" <<EOS
#!/usr/bin/env bash
export HF_HOME="$DEST/hf" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
exec "$DEST/venv/bin/python" "$DEST/skriva.py" "\$@"
EOS
chmod +x "$BIN/skriva"; ln -sf "$BIN/skriva" "$BIN/skriva.py"
case ":$PATH:" in *":$BIN:"*) ;; *) grep -qs "$BIN" "$HOME/.zshrc" || echo "export PATH=\"$BIN:\$PATH\"" >> "$HOME/.zshrc"; echo "Added $BIN to PATH in ~/.zshrc - open a new Terminal window.";; esac
echo "Done. Usage: skriva interview_01.mp3"
