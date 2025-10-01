#!/usr/bin/env bash
set -euo pipefail

# Make sure we can see where uv usually installs
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

if ! command -v uv >/dev/null 2>&1; then
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # refresh PATH for the current shell (installer places uv in ~/.local/bin or ~/.cargo/bin)
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi

# Resolve uv explicitly if command -v still fails
UV_BIN="$(command -v uv || true)"
if [ -z "$UV_BIN" ]; then
  for p in "$HOME/.local/bin/uv" "$HOME/.cargo/bin/uv" "/usr/local/bin/uv" "/opt/homebrew/bin/uv"; do
    if [ -x "$p" ]; then UV_BIN="$p"; break; fi
  done
fi

if [ -z "$UV_BIN" ]; then
  echo "❌ uv still not found after install."
  echo "Contents of ~/.local/bin and ~/.cargo/bin (for debugging):"
  ls -lah "$HOME/.local/bin" || true
  ls -lah "$HOME/.cargo/bin" || true
  exit 1
fi

echo "Using uv at: $UV_BIN"
"$UV_BIN" --version

echo "Creating Python 3.12 venv..."
"$UV_BIN" venv --python 3.12 .venv

# Activate now (optional)
# shellcheck disable=SC1091
source .venv/bin/activate
python --version

# Sync dependencies from pyproject.toml (if exists)
if [ -f pyproject.toml ]; then
  echo "Syncing project dependencies..."
  uv sync
fi

# Ensure data and outputs directories exist
mkdir -p data outputs

# Download dataset
echo "Downloading MATH.zip..."
wget -O MATH.zip https://www.modelscope.cn/datasets/opencompass/competition_math/resolve/master/data/MATH.zip

# Extract with Python, move to data/, and clean up
echo "Extracting dataset with Python..."
python3 - <<'EOF'
import zipfile, pathlib, shutil

zip_path = pathlib.Path("MATH.zip")
out_dir = pathlib.Path("data")

with zipfile.ZipFile(zip_path, "r") as zf:
    zf.extractall(".")

# Assume the extracted folder is named "MATH"
extracted = pathlib.Path("MATH")
if extracted.exists():
    target = out_dir / extracted.name
    if target.exists():
        shutil.rmtree(target)  # overwrite if already exists
    shutil.move(str(extracted), str(out_dir))

# Remove the zip file
zip_path.unlink()
print("✅ Unzipped to", out_dir.resolve(), "and removed", zip_path.name)
EOF

echo "✅ Setup complete! Data in ./data/MATH and outputs/ ready."
