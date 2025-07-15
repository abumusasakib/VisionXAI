import os
import json
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Union, Dict, List, Tuple # Added Dict, List, Tuple for type hinting

# Import the JSONCaptionParser from the project's caption_parsers module.
# Ensure that 'caption_parsers/json_parser.py' exists relative to where this script is run.
from caption_parsers.json_parser import JSONCaptionParser


# Define the target size for image resizing
IMAGE_SIZE: Tuple[int, int] = (299, 299)

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
            # Check if the image is already clean (RGB, no ICC profile, no palette)
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
    Returns a black (zero-filled) image on error.

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
    
def validate_sequential_dataset(dataset_dir: str, apply_preprocessing: bool = False, apply_image_decoding: bool = False):
    """
    Validates a sequential image-caption dataset using JSONCaptionParser,
    optionally applying PNG preprocessing and checking image readability.

    Args:
        dataset_dir (str): Directory with `images/` and `captions.json`.
        apply_preprocessing (bool): Whether to apply PNG preprocessing to images.
        apply_image_decoding (bool): Whether to perform a detailed check of image readability
                                     by attempting to decode and resize each image.
    """
    image_dir = os.path.join(dataset_dir, "images")
    caption_path = os.path.join(dataset_dir, "captions.json")

    # Check for essential dataset components
    if not os.path.exists(image_dir) or not os.path.exists(caption_path):
        print(f"❌ Error: Missing 'images/' or 'captions.json' in {dataset_dir}")
        return

    print(f"\n🔍 Validating dataset at: {dataset_dir}")

    # Use JSONCaptionParser to extract captions
    json_parser = JSONCaptionParser()
    # We pass validate_images=False here because the main script will do its own detailed checks.
    caption_mapping: Dict[str, List[str]] = json_parser.extract(caption_path, images_path=image_dir, validate_images=False)

    # Check if the caption mapping is empty, indicating a parsing error or empty file
    if not caption_mapping:
        print("❌ Error: No captions were extracted. Please check your captions.json file and image_dir path.")
        return


    # Validate image filename sequencing
    # The `caption_mapping` keys are already absolute paths like 'dataset_dir/images/1.png'
    # We need to extract just the stem (e.g., '1') for sorting and checking sequential order.
    # We filter for .png files in the image_dir itself for a more direct check of existing image files
    image_files_on_disk = sorted(
        [f for f in os.listdir(image_dir) if f.lower().endswith(".png")], # Case-insensitive check
        key=lambda x: int(Path(x).stem) # Sort by the numerical part of the filename
    )

    are_filenames_sequential = all(
        int(Path(fname).stem) == i for i, fname in enumerate(image_files_on_disk, 1)
    )
    print(f"🔢 Image filenames on disk sequential (1 to N)? {are_filenames_sequential}")
    if not are_filenames_sequential and image_files_on_disk:
        print(f"   (Found start: {int(Path(image_files_on_disk[0]).stem)}, end: {int(Path(image_files_on_disk[-1]).stem)})")


    # Validate caption sequencing by checking the numerical part of image filenames referenced in captions.json
    # The keys of caption_mapping are already absolute paths (e.g., /path/to/dataset/images/1.png)
    caption_indices = sorted(int(Path(img_path).stem) for img_path in caption_mapping.keys())
    are_captions_sequential = caption_indices == list(range(1, len(caption_mapping) + 1))
    print(f"📝 Captions sequentially indexed (1 to N in JSON)? {are_captions_sequential}")
    if not are_captions_sequential and caption_indices:
        print(f"   (Found start: {caption_indices[0]}, end: {caption_indices[-1]})")

    # Perform optional image readability checks
    if apply_image_decoding:
        missing_images = []
        unreadable_images = []

        print("\n🔎 Checking images for existence and readability...")
        # Iterate directly over the absolute image paths obtained from the parser
        for i, img_path_abs in enumerate(caption_mapping.keys(), 1):
            # The path is already absolute, so just check existence
            if not os.path.exists(img_path_abs):
                missing_images.append(img_path_abs)
                continue # Skip further checks for missing images

            if apply_preprocessing and img_path_abs.lower().endswith(".png"):
                preprocess_image(img_path_abs)

            img_array = decode_and_resize(img_path_abs)
            if np.count_nonzero(img_array) == 0:
                unreadable_images.append(img_path_abs)

            if i % 500 == 0 or i == len(caption_mapping):
                print(f"\r  → Checked {i}/{len(caption_mapping)} images", end='', flush=True)

        print("\n\n📊 Image Readability Summary:")
        print(f"🖼️  Total unique images referenced in JSON: {len(caption_mapping)}")
        print(f"✅ Found & readable: {len(caption_mapping) - len(missing_images) - len(unreadable_images)}")
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
    else:
        print("\nImage readability check skipped as per user choice.")

# === Entry point ===
if __name__ == "__main__":
    print("--- Sequential Image Dataset Validator ---")
    print("This script validates image and caption sequencing and can optionally check image readability.")

    dataset_path_input = input("📁 Enter dataset folder path (e.g., 'my_dataset_root/'): ").strip()
    
    # Preprocessing choice
    preprocess_choice = input("⚙️  Do you want to preprocess PNGs to suppress ICC warnings? (yes/no): ").strip().lower()
    apply_preprocessing = preprocess_choice in {"yes", "y"}

    # Image decoding/readability validation choice
    decoding_choice = input("🧪 Do you want to validate image readability (this involves decoding each image)? (yes/no): ").strip().lower()
    apply_image_decoding = decoding_choice in {"yes", "y"}

    validate_sequential_dataset(
        dataset_path_input, # Use the user's input directly, Path().resolve() can be handled inside if needed
        apply_preprocessing=apply_preprocessing,
        apply_image_decoding=apply_image_decoding
    )
    print("\nValidation complete.")
