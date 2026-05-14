# merge_back_bg.py

Batch process multiple `back.png` files by placing them centered on top of a stretched background image.

The script:

- Reads all folders inside `input/`
- Finds `back.png` inside each folder
- Resizes:
  - `bg.png` → `55mm x 87mm`
  - `back.png` → `50mm x 80mm`
- Centers `back.png` on `bg.png`
- Saves output to `out/<folder_name>/back.png`

---

# Folder Structure

```text
project/
│
├── bg.png
├── merge_back_bg.py
├── input/
│   ├── folder1/
│   │   └── back.png
│   ├── folder2/
│   │   └── back.png
│   └── folder3/
│       └── back.png
```

---

# Install UV

Install UV if not already installed:

## Linux / macOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Windows (PowerShell)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Official website:

- https://github.com/astral-sh/uv

---

# Create Virtual Environment

```bash
uv venv
```

Activate environment:

## Linux / macOS

```bash
source .venv/bin/activate
```

## Windows

```powershell
.venv\Scripts\activate
```

---

# Install Dependencies

```bash
uv pip install pillow
```

---

# Run Script

```bash
python merge_back_bg.py
```

or with UV:

```bash
uv run merge_back_bg.py
```

---

# Output Structure

```text
out/
├── folder1/
│   └── back.png
├── folder2/
│   └── back.png
└── folder3/
    └── back.png
```

---

# How To Change Sizes

Open `merge_back_bg.py`.

Edit these values:

```python
BG_SIZE_MM = (55, 87)
BACK_SIZE_MM = (50, 80)
```

Format:

```python
(width_mm, height_mm)
```

Example:

```python
BG_SIZE_MM = (60, 90)
BACK_SIZE_MM = (52, 82)
```

---

# Change DPI

Default DPI is:

```python
DPI = 300
```

Higher DPI = larger image resolution.

Common values:

- `300` → print quality
- `600` → high print quality
- `150` → smaller files

---

# Notes

- Images are stretched exactly to target size
- Aspect ratio is NOT preserved
- Output folders are created automatically
- Existing files in `out/` will be overwritten

---

# Required Python Version

Recommended:

- Python 3.10+
```
