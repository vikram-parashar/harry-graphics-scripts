from pathlib import Path
from PIL import Image

# =========================================================
# CONFIG
# =========================================================

INPUT_DIR = "/home/vikram/Downloads/sample"
OUTPUT_DIR = "out"
DPI = 300

# A3 size in mm
SHEET_WIDTH_MM = 304.8
SHEET_HEIGHT_MM = 457.2

# Card size in mm
CARD_W_MM = 55
CARD_H_MM = 87

# Gap between cards
GAP_MM = 1

# Grid
ROWS = 5
COLS = 5
CARDS_PER_SHEET = ROWS * COLS

# Front layout order
FRONT_LAYOUT = [
    [0, 1, 2, 3, 4],
    [5, 6, 7, 8, 9],
    [10, 11, 12, 13, 14],
    [15, 16, 17, 18, 19],
    [20, 21, 22, 23, 24],
]

# Back layout order
BACK_LAYOUT = [
    [4, 3, 2, 1, 0],
    [9, 8, 7, 6, 5],
    [14, 13, 12, 11, 10],
    [19, 18, 17, 16, 15],
    [24, 23, 22, 21, 20],
]

# =========================================================
# HELPERS
# =========================================================


def mm_to_px(mm, dpi=DPI):
    return int((mm / 25.4) * dpi)


A3_W = mm_to_px(SHEET_WIDTH_MM)
A3_H = mm_to_px(SHEET_HEIGHT_MM)

CARD_W = mm_to_px(CARD_W_MM)
CARD_H = mm_to_px(CARD_H_MM)

GAP = mm_to_px(GAP_MM)

GRID_W = (COLS * CARD_W) + ((COLS - 1) * GAP)
GRID_H = (ROWS * CARD_H) + ((ROWS - 1) * GAP)

OFFSET_X = (A3_W - GRID_W) // 2
OFFSET_Y = (A3_H - GRID_H) // 2


# =========================================================
# LOAD CARD FOLDERS
# =========================================================

input_path = Path(INPUT_DIR)
output_path = Path(OUTPUT_DIR)
output_path.mkdir(exist_ok=True)

cardsFolder = []

for item in sorted(input_path.iterdir()):
    if item.is_dir():
        front = item / "front.png"
        back = item / "back.png"

        if front.exists() and back.exists():
            cardsFolder.append(
                {
                    "code": item.name,
                    "front": front,
                    "back": back,
                }
            )

print(f"Found {len(cardsFolder)} cards")


# =========================================================
# CHUNKING
# =========================================================


def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


chunks = list(chunk_list(cardsFolder, CARDS_PER_SHEET))


# =========================================================
# SHEET CREATION
# =========================================================


def create_sheet(chunk, layout, side="front"):
    sheet = Image.new("RGB", (A3_W, A3_H), "white")

    for row_idx, row in enumerate(layout):
        for col_idx, card_index in enumerate(row):
            if card_index >= len(chunk):
                continue

            card = chunk[card_index]

            img_path = card[side]
            img = Image.open(img_path).convert("RGB")

            # Resize to exact tile size
            img = img.resize((CARD_W, CARD_H), Image.LANCZOS)

            x = OFFSET_X + col_idx * (CARD_W + GAP)
            y = OFFSET_Y + row_idx * (CARD_H + GAP)

            sheet.paste(img, (x, y))

    return sheet


# =========================================================
# GENERATE SHEETS
# =========================================================

for chunk_index, chunk in enumerate(chunks, start=1):
    # Front sheet
    front_sheet = create_sheet(chunk, FRONT_LAYOUT, side="front")

    front_output = output_path / f"Sheet_{chunk_index:03d}_Fr.png"
    front_sheet.save(front_output, dpi=(DPI, DPI))

    # Back sheet
    back_sheet = create_sheet(chunk, BACK_LAYOUT, side="back")

    back_output = output_path / f"Sheet_{chunk_index:03d}_Br.png"
    back_sheet.save(back_output, dpi=(DPI, DPI))

    print(f"Generated set {chunk_index}")

print("Done")
