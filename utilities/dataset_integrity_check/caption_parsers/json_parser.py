import json
import os
from pathlib import Path
from typing import Dict, List
from caption_parsers.caption_parser import CaptionParser


class JSONCaptionParser(CaptionParser):
    """
    A concrete implementation of CaptionParser for JSON files.

    This parser expects a JSON file containing a list of objects, where each object
    has a 'filename' key (for the image name) and a 'caption' key (which is a list of captions).
    Example JSON structure:
    [
        {"filename": "image1.jpg", "caption": ["caption for image1", "another caption"]},
        {"filename": "image2.jpg", "caption": ["caption for image2"]}
    ]
    """

    def extract(self, file_path: str, images_path: str = "", validate_images: bool = True) -> Dict[str, List[str]]:
        """
        Extracts image filenames and their associated captions from a JSON file.

        Args:
            file_path (str): The full path to the JSON caption file.
            images_path (str, optional): The base directory where images referenced in the JSON
                                         are located. This path is prepended to filenames from the JSON.
                                         Defaults to "".
            validate_images (bool, optional): If True, checks if the image file exists on disk
                                              before adding its captions to the mapping. Defaults to True.

        Returns:
            Dict[str, List[str]]: A dictionary mapping absolute image paths to a list of their captions.
                                  Captions are formatted with leading/trailing spaces as per the original code.
        """
        caption_mapping: Dict[str, List[str]] = {}
        print(f"\n➡️  Parsing JSON: {os.path.basename(file_path)}...")
        try:
            with open(file_path, encoding="utf8") as caption_file:
                caption_data = json.load(caption_file)

                # Ensure caption_data is iterable (e.g., a list of dictionaries)
                if not isinstance(caption_data, list):
                    print(f"Warning: JSON file {file_path} does not contain a list at its root. Skipping.")
                    return caption_mapping

                for idx, item in enumerate(caption_data):
                    if idx % 1000 == 0:
                        print(f"\r  → Processing JSON item {idx}...", end="", flush=True)

                    if not isinstance(item, dict) or 'filename' not in item or 'caption' not in item:
                        print(f"\nWarning: Skipping malformed JSON item in {file_path}: {item}")
                        continue

                    # Construct the full image path
                    img_name_from_json = item['filename'].strip()
                    img_name_abs = os.path.join(images_path, img_name_from_json)

                    # Ensure captions is a list, even if it's a single string
                    raw_captions = item['caption']
                    if not isinstance(raw_captions, list):
                        raw_captions = [raw_captions] # Convert single string to list

                    # Format captions
                    formatted_captions = ["<start>" + str(caption).strip() + " " for caption in raw_captions if caption is not None]

                    # Validate image existence if required
                    if not validate_images or Path(img_name_abs).exists():
                        if formatted_captions: # Only add if there are valid captions
                            caption_mapping[img_name_abs] = formatted_captions
                    else:
                        # print(f"Warning: Image not found for {img_name_abs}. Skipping.")
                        pass # Suppress warning for missing images during non-validation pass

            print(f"\r  → Finished parsing {os.path.basename(file_path)}. Total valid entries: {len(caption_mapping)}.", flush=True)

        except json.JSONDecodeError as e:
            print(f"\nError: Invalid JSON format in {file_path}: {e}")
        except Exception as e:
            print(f"\nError reading JSON file {file_path}: {e}")

        return caption_mapping