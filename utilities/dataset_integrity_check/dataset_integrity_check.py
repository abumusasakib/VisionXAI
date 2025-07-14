import os
import json
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Union

IMAGE_SIZE = (299, 299)


def preprocess_image(image_path: str):
    """
    Preprocess PNG image by stripping ICC profile to suppress warnings.
    Skips if already RGB and no ICC profile or palette.

    Args:
        image_path (str): Path to image file.
    """
    try:
        if not Path(image_path).exists():
            return

        with Image.open(image_path) as img:
            if img.mode == "RGB" and not img.info.get("icc_profile") and not img.palette:
                return  # Already clean

            img = img.convert("RGB")
            img.save(image_path, "PNG", icc_profile=None)
            print(f"\r  → Preprocessed PNG: {os.path.basename(image_path)}", end='', flush=True)

    except Exception as e:
        print(f"\nError preprocessing image {image_path}: {e}")


def decode_and_resize(img_path: Union[str, bytes]) -> np.ndarray:
    """
    Decode image using OpenCV, convert to RGB, resize to IMAGE_SIZE, return float32 array.
    Returns black image on error.

    Args:
        img_path (Union[str, bytes]): Path to image.

    Returns:
        np.ndarray: RGB image as float32 or zeros on failure.
    """
    try:
        if isinstance(img_path, bytes):
            img_path = img_path.decode("utf-8")

        img = cv2.imread(img_path, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Could not read image")

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, IMAGE_SIZE)

        return img.astype(np.float32)
    except Exception as e:
        print(f"\n⚠️ Error decoding image '{img_path}': {e}")
        return np.zeros((*IMAGE_SIZE, 3), dtype=np.float32)


def validate_sequential_dataset(dataset_dir: str, apply_preprocessing: bool = False):
    """
    Validates sequential image-caption dataset, optionally applying PNG preprocessing.

    Args:
        dataset_dir (str): Directory with `images/` and `captions.json`.
        apply_preprocessing (bool): Whether to apply PNG preprocessing.
    """
    image_dir = os.path.join(dataset_dir, "images")
    caption_path = os.path.join(dataset_dir, "captions.json")

    if not os.path.exists(image_dir) or not os.path.exists(caption_path):
        print(f"❌ Error: Missing 'images/' or 'captions.json' in {dataset_dir}")
        return

    print(f"\n🔍 Validating dataset at: {dataset_dir}")

    image_files = sorted(
        [f for f in os.listdir(image_dir) if f.endswith(".png")],
        key=lambda x: int(Path(x).stem)
    )

    are_filenames_sequential = all(
        int(fname.split('.')[0]) == i for i, fname in enumerate(image_files, 1)
    )
    print(f"🔢 Image filenames sequential? {are_filenames_sequential}")

    with open(caption_path, encoding="utf-8") as f:
        caption_data = json.load(f)

    caption_indices = sorted(int(item["filename"].split(".")[0]) for item in caption_data)
    are_captions_sequential = caption_indices == list(range(1, len(caption_data) + 1))
    print(f"📝 Captions sequential? {are_captions_sequential}")

    missing_images = []
    unreadable_images = []

    print("\n🔎 Checking images...")
    for i, item in enumerate(caption_data, 1):
        img_filename = item["filename"].strip()
        img_path = os.path.join(image_dir, img_filename)

        if not os.path.exists(img_path):
            missing_images.append(img_path)
            continue

        if apply_preprocessing and img_path.endswith(".png"):
            preprocess_image(img_path)

        img_array = decode_and_resize(img_path)
        if np.count_nonzero(img_array) == 0:
            unreadable_images.append(img_path)

        if i % 500 == 0 or i == len(caption_data):
            print(f"\r  → Checked {i}/{len(caption_data)} images", end='', flush=True)

    print("\n\n📊 Summary:")
    print(f"🖼️  Total images in JSON: {len(caption_data)}")
    print(f"✅ Found & readable: {len(caption_data) - len(missing_images) - len(unreadable_images)}")
    print(f"❌ Missing: {len(missing_images)}")
    print(f"⚠️ Unreadable: {len(unreadable_images)}")

    if missing_images:
        print("\n🚫 Sample missing images:")
        for path in missing_images[:5]:
            print(f"  - {path}")

    if unreadable_images:
        print("\n🛑 Sample unreadable images:")
        for path in unreadable_images[:5]:
            print(f"  - {path}")


# === Entry point ===
if __name__ == "__main__":
    dataset_path = input("📁 Enter dataset folder path (should contain 'images/' and 'captions.json'): ").strip()
    preprocess_choice = input("⚙️  Do you want to preprocess PNGs to suppress ICC warnings? (yes/no): ").strip().lower()
    apply_preprocessing = preprocess_choice in {"yes", "y"}

    validate_sequential_dataset(dataset_path, apply_preprocessing=apply_preprocessing)
