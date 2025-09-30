#!/usr/bin/env bash
set -euo pipefail

# Download uv if not already installed
if ! command -v uv &>/dev/null; then
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create Python 3.12 virtual environment
echo "Creating Python 3.12 venv..."
uv venv --python 3.12

# Activate the venv
source .venv/bin/activate

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
