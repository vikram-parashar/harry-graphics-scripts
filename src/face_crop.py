from pathlib import Path
import math

import cv2
import mediapipe as mp
import numpy as np

# ============================================================
# CONFIG
# ============================================================

INPUT_DIR = "/home/vikram/Downloads/emeraldschool/"
OUTPUT_DIR = "cropped_photos"

TARGET_WIDTH = 700
TARGET_HEIGHT = 800

# Smart crop tuning
TOP_PADDING = 0.7
BOTTOM_PADDING = 0.9
SIDE_PADDING = 0.45

# Optional face alignment
ENABLE_ALIGNMENT = True

# ============================================================
# MEDIAPIPE SETUP
# ============================================================

mp_face_detection = mp.solutions.face_detection
mp_face_mesh = mp.solutions.face_mesh

face_detector = mp_face_detection.FaceDetection(
    model_selection=1,
    min_detection_confidence=0.6,
)

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,
)

# ============================================================
# UTILS
# ============================================================


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def load_image(path):
    img = cv2.imread(str(path))
    if img is None:
        raise ValueError(f"Could not load image: {path}")
    return img


def save_image(path, image):
    cv2.imwrite(str(path), image)


def rotate_image(image, angle, center):
    h, w = image.shape[:2]

    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    cos = abs(matrix[0, 0])
    sin = abs(matrix[0, 1])

    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    matrix[0, 2] += (new_w / 2) - center[0]
    matrix[1, 2] += (new_h / 2) - center[1]

    rotated = cv2.warpAffine(
        image,
        matrix,
        (new_w, new_h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT,
    )

    return rotated


def get_face_detection(image):
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = face_detector.process(rgb)

    if not result.detections:
        return None

    h, w = image.shape[:2]

    detection = result.detections[0]
    bbox = detection.location_data.relative_bounding_box

    x = int(bbox.xmin * w)
    y = int(bbox.ymin * h)
    bw = int(bbox.width * w)
    bh = int(bbox.height * h)

    return (x, y, bw, bh)


def get_eye_centers(image):
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb)

    if not result.multi_face_landmarks:
        return None

    landmarks = result.multi_face_landmarks[0]

    h, w = image.shape[:2]

    LEFT_EYE = [33, 133]
    RIGHT_EYE = [362, 263]

    def avg_point(indices):
        xs = []
        ys = []

        for idx in indices:
            lm = landmarks.landmark[idx]
            xs.append(lm.x * w)
            ys.append(lm.y * h)

        return np.mean(xs), np.mean(ys)

    left_eye = avg_point(LEFT_EYE)
    right_eye = avg_point(RIGHT_EYE)

    return left_eye, right_eye


def align_face(image):
    eyes = get_eye_centers(image)

    if eyes is None:
        return image

    left_eye, right_eye = eyes

    dx = right_eye[0] - left_eye[0]
    dy = right_eye[1] - left_eye[1]

    angle = math.degrees(math.atan2(dy, dx))

    eye_center = (
        int((left_eye[0] + right_eye[0]) / 2),
        int((left_eye[1] + right_eye[1]) / 2),
    )

    rotated = rotate_image(image, angle, eye_center)

    return rotated


def expand_crop(x, y, w, h):
    x1 = x - int(w * SIDE_PADDING)
    y1 = y - int(h * TOP_PADDING)

    x2 = x + w + int(w * SIDE_PADDING)
    y2 = y + h + int(h * BOTTOM_PADDING)

    return x1, y1, x2, y2


def adjust_to_aspect_ratio(x1, y1, x2, y2, target_ratio):
    crop_w = x2 - x1
    crop_h = y2 - y1

    current_ratio = crop_w / crop_h

    if current_ratio < target_ratio:
        # Too narrow -> widen
        new_w = int(crop_h * target_ratio)
        diff = new_w - crop_w

        x1 -= diff // 2
        x2 += diff - diff // 2

    else:
        # Too wide -> increase height
        new_h = int(crop_w / target_ratio)
        diff = new_h - crop_h

        y1 -= diff // 2
        y2 += diff - diff // 2

    return x1, y1, x2, y2


def crop_with_padding(image, x1, y1, x2, y2):
    h, w = image.shape[:2]

    pad_left = max(0, -x1)
    pad_top = max(0, -y1)
    pad_right = max(0, x2 - w)
    pad_bottom = max(0, y2 - h)

    if any([pad_left, pad_top, pad_right, pad_bottom]):
        image = cv2.copyMakeBorder(
            image,
            pad_top,
            pad_bottom,
            pad_left,
            pad_right,
            borderType=cv2.BORDER_REFLECT,
        )

    x1 += pad_left
    x2 += pad_left
    y1 += pad_top
    y2 += pad_top

    cropped = image[y1:y2, x1:x2]

    return cropped


def process_image(path, output_dir):
    print(f"Processing: {path.name}")

    image = load_image(path)

    if ENABLE_ALIGNMENT:
        image = align_face(image)

    detection = get_face_detection(image)

    if detection is None:
        print(f"  No face detected.")
        return

    x, y, w, h = detection

    x1, y1, x2, y2 = expand_crop(x, y, w, h)

    target_ratio = TARGET_WIDTH / TARGET_HEIGHT

    x1, y1, x2, y2 = adjust_to_aspect_ratio(
        x1,
        y1,
        x2,
        y2,
        target_ratio,
    )

    cropped = crop_with_padding(
        image,
        x1,
        y1,
        x2,
        y2,
    )

    resized = cv2.resize(
        cropped,
        (TARGET_WIDTH, TARGET_HEIGHT),
        interpolation=cv2.INTER_LANCZOS4,
    )

    output_path = Path(output_dir) / path.name

    save_image(output_path, resized)

    print(f"  Saved -> {output_path}")


# ============================================================
# MAIN
# ============================================================


def main():
    ensure_dir(OUTPUT_DIR)

    supported = {".jpg", ".jpeg", ".png", ".webp"}

    paths = [p for p in Path(INPUT_DIR).iterdir() if p.suffix.lower() in supported]

    print(f"Found {len(paths)} images")

    for path in paths:
        try:
            process_image(path, OUTPUT_DIR)
        except Exception as e:
            print(f"Error processing {path.name}: {e}")


if __name__ == "__main__":
    main()
