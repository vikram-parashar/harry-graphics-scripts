from pathlib import Path
from PIL import Image

# =========================================================
# SCRIPT NAME
# =========================================================
# id_card_sheet_generator.py
#
# WHAT IT DOES:
# - Reads folders containing:
#       front.png
#       back.png
#
# - Creates printable A3 sheets
# - Generates:
#       Sheet_001_Fr.png
#       Sheet_001_Br.png
#
# - Uses mirrored back layout for duplex printing
#
# =========================================================

# =========================================================
# USER INPUT
# =========================================================

INPUT_DIR = Path("/home/vikram/dev/harry-graphics-scripts/out/UDAIPURWATI/")

OUTPUT_DIR = Path("/home/vikram/dev/harry-graphics-scripts/tiles/udaipurwati/")

input_path = Path(INPUT_DIR)
output_path = Path(OUTPUT_DIR)

front_output_dir = output_path / "front"
back_output_dir = output_path / "back"

# ---------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------

if not input_path.exists():
    print("\nERROR: Input folder does not exist.")
    input("Press ENTER to exit...")
    exit()

front_output_dir.mkdir(parents=True, exist_ok=True)
back_output_dir.mkdir(parents=True, exist_ok=True)

# =========================================================
# CONFIG
# =========================================================

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

# =========================================================
# FRONT LAYOUT
# =========================================================

FRONT_LAYOUT = [
    [0, 1, 2, 3, 4],
    [5, 6, 7, 8, 9],
    [10, 11, 12, 13, 14],
    [15, 16, 17, 18, 19],
    [20, 21, 22, 23, 24],
]

# =========================================================
# BACK LAYOUT
# =========================================================

BACK_LAYOUT = [
    [4, 3, 2, 1, 0],
    [9, 8, 7, 6, 5],
    [14, 13, 12, 11, 10],
    [19, 18, 17, 16, 15],
    [24, 23, 22, 21, 20],
]

# =========================================================
# DISPLAY SETTINGS
# =========================================================

print("\n" + "=" * 70)
print("ID CARD SHEET GENERATOR SETTINGS")
print("=" * 70)

print(f"INPUT FOLDER        : {INPUT_DIR}")
print(f"OUTPUT FOLDER       : {OUTPUT_DIR}")

print("\nSHEET SETTINGS")
print(f"SHEET SIZE          : {SHEET_WIDTH_MM} mm x {SHEET_HEIGHT_MM} mm")
print(f"DPI                 : {DPI}")

print("\nCARD SETTINGS")
print(f"CARD SIZE           : {CARD_W_MM} mm x {CARD_H_MM} mm")
print(f"GAP                 : {GAP_MM} mm")

print("\nGRID SETTINGS")
print(f"ROWS                : {ROWS}")
print(f"COLUMNS             : {COLS}")
print(f"CARDS PER SHEET     : {CARDS_PER_SHEET}")

print("\nINPUT STRUCTURE")
print("Folder/")
print("   Card001/")
print("       front.png")
print("       back.png")

print("\nOUTPUT FILES")
print("Sheet_001_Fr.png")
print("Sheet_001_Br.png")

print("=" * 70)

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

# ---------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------

if not input_path.exists():
    print("\nERROR: Input folder does not exist.")
    input("Press ENTER to exit...")
    exit()

output_path.mkdir(parents=True, exist_ok=True)

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

print(f"\nFound {len(cardsFolder)} cards")

if len(cardsFolder) == 0:
    print("\nERROR: No valid card folders found.")
    input("Press ENTER to exit...")
    exit()

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

            # Resize card
            img = img.resize((CARD_W, CARD_H), Image.LANCZOS)

            x = OFFSET_X + col_idx * (CARD_W + GAP)
            y = OFFSET_Y + row_idx * (CARD_H + GAP)

            sheet.paste(img, (x, y))

    return sheet


# =========================================================
# GENERATE SHEETS
# =========================================================

print("\nGenerating sheets...\n")

for chunk_index, chunk in enumerate(chunks, start=1):
    # -----------------------------------------------------
    # FRONT SHEET
    # -----------------------------------------------------

    front_sheet = create_sheet(chunk, FRONT_LAYOUT, side="front")

    front_output = front_output_dir / f"Sheet_{chunk_index:03d}.png"

    front_sheet.save(front_output, dpi=(DPI, DPI))

    # -----------------------------------------------------
    # BACK SHEET
    # -----------------------------------------------------

    back_sheet = create_sheet(chunk, BACK_LAYOUT, side="back")

    back_output = back_output_dir / f"Sheet_{chunk_index:03d}.png"

    back_sheet.save(back_output, dpi=(DPI, DPI))

    print(f"Generated set {chunk_index}")

# =========================================================
# DONE
# =========================================================

print("\n" + "=" * 70)
print("PROCESS COMPLETED.")
print("=" * 70)

input("\nPress ENTER to exit...")
