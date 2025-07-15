import os
import zipfile
import xml.etree.ElementTree as ET  # Standard ElementTree is used for XML parsing
import csv
import json
from pathlib import Path
from collections import defaultdict
from typing import Set, List, Dict, Optional
from abc import ABC, abstractmethod

# --- Constants ---
# Set of common image file extensions
IMAGE_EXTENSIONS: Set[str] = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}

# --- Helper Functions ---
def is_image_file(filename: str) -> bool:
    """
    Checks if a given filename has a recognized image extension.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file is an image, False otherwise.
    """
    return os.path.splitext(filename)[1].lower() in IMAGE_EXTENSIONS

def get_extension(filename: str) -> str:
    """
    Extracts the lowercase extension of a file.

    Args:
        filename (str): The name of the file.

    Returns:
        str: The lowercase file extension (e.g., '.jpg').
    """
    return os.path.splitext(filename)[1].lower()

# --- Abstraction for Caption Reference Extraction ---
class CaptionReferenceExtractor(ABC):
    """
    Abstract Base Class for extracting image filenames referenced within a caption file.
    """
    @abstractmethod
    def extract(self, filepath: str) -> Set[str]:
        """
        Extracts a set of unique image filenames referenced in the given file.

        Args:
            filepath (str): The path to the caption file.

        Returns:
            Set[str]: A set of unique image filenames.
        """
        pass

class XLSXReferenceExtractor(CaptionReferenceExtractor):
    """
    Extracts image filenames referenced in an XLSX file.
    Assumes image names are in the first column and may be followed by '#'.
    Handles XLSX as a ZIP file containing XML data. Also converts "MG" to "IMG_".
    """

    def __init__(self, has_header: bool = True):
        """
        Initializes the XLSXCaptionParser.

        Args:
            has_header (bool, optional): Specifies if the XLSX file has a header row.
                                        If True, the first row is skipped during parsing. Defaults to True.
        """
        self.has_header = has_header

    def extract(self, filepath: str) -> Set[str]:
        referenced_images: Set[str] = set()
        try:
            with zipfile.ZipFile(filepath, "r") as xlsx:
                sheet_file = "xl/worksheets/sheet1.xml"
                shared_strings_file = "xl/sharedStrings.xml"
                ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

                shared_strings: List[str] = []
                if shared_strings_file in xlsx.namelist():
                    with xlsx.open(shared_strings_file) as f:
                        tree = ET.parse(f)
                        shared_strings = [t.text for t in tree.findall(f".//{ns}t") if t.text is not None]

                if sheet_file not in xlsx.namelist():
                    print(f"Warning: Worksheet '{sheet_file}' not found in {filepath}")
                    return referenced_images

                with xlsx.open(sheet_file) as f:
                    tree = ET.parse(f)
                    rows = tree.findall(f".//{ns}row")
                    # Determine the starting row based on whether a header is present.
                    start_row = 1 if self.has_header and len(rows) > 0 else 0

                    for row in rows[start_row:]:
                        # Find all 'c' elements (cells) within the row
                        cells = [el for el in row if el.tag.endswith("c")]
                        if not cells:
                            continue # Skip empty rows

                        cell = cells[0] # Assume image name is in the first column
                        cell_type = cell.get("t") # 's' for shared string, 'n' for number, etc.
                        value_elem = next((v for v in cell if v.tag.endswith("v")), None) # Cell value element

                        if value_elem is not None and value_elem.text:
                            val: Optional[str] = None
                            if cell_type == "s": # If it's a shared string, look up its value
                                try:
                                    idx = int(value_elem.text)
                                    val = shared_strings[idx] if 0 <= idx < len(shared_strings) else None
                                except (ValueError, IndexError):
                                    pass # Invalid index or not an integer
                            else: # Otherwise, take the value directly
                                val = value_elem.text

                            if val:
                                # Extract image name by splitting at '#' and replace 'MG' with 'IMG_'
                                img_name = val.split("#")[0].replace("MG", "IMG_").strip()
                                referenced_images.add(img_name)

        except zipfile.BadZipFile:
            print(f"\n[XLSX] Error: {filepath} is not a valid zip file (corrupted XLSX).")
        except Exception as e:
            print(f"\n[XLSX] An error occurred while reading {filepath}: {e}")
        return referenced_images

class CSVReferenceExtractor(CaptionReferenceExtractor):
    """
    Extracts image filenames referenced in a CSV file.
    Assumes image names are in a column named "caption_id" and may be followed by '#'.
    """
    def extract(self, filepath: str) -> Set[str]:
        referenced_images: Set[str] = set()
        try:
            with open(filepath, encoding="utf-8", newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    val = row.get("caption_id", "") # Get value from 'caption_id' column
                    if val:
                        img_name = val.split("#")[0].strip() # Split at '#' to get image name
                        referenced_images.add(img_name)
        except FileNotFoundError:
            print(f"\n[CSV] Error: File not found at {filepath}")
        except Exception as e:
            print(f"\n[CSV] An error occurred while reading {filepath}: {e}")
        return referenced_images

class JSONReferenceExtractor(CaptionReferenceExtractor):
    """
    Extracts image filenames referenced in a JSON file.
    Assumes each item in the JSON list has a "filename" key.
    """
    def extract(self, filepath: str) -> Set[str]:
        referenced_images = set()
        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
                # Assuming data is a list of dictionaries, each with a 'filename' key
                for item in data:
                    img_name = item.get("filename", "").strip()
                    if img_name:
                        referenced_images.add(img_name)
        except Exception as e:
            print(f"\n[JSON] Error reading {filepath}: {e}")
        return referenced_images

class TXTReferenceExtractor(CaptionReferenceExtractor):
    """
    Extracts image filenames referenced in a plain TXT file.
    Assumes each line is formatted as "image_filename   caption_text" (three spaces).
    """
    def extract(self, filepath: str) -> Set[str]:
        referenced_images = set()
        try:
            with open(filepath, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue # Skip empty lines

                    parts = line.split("   ", 1) # Split by exactly three spaces
                    if len(parts) < 2:
                        # print(f"Warning: Skipping malformed line in TXT: '{line}'")
                        continue # Skip malformed lines

                    img_name = parts[0].strip()
                    referenced_images.add(img_name)
        except Exception as e:
            print(f"\n[TXT] Error reading {filepath}: {e}")
        return referenced_images

def print_tree_and_count(path: str, prefix: str, output_lines: List[str], all_images_on_disk: Set[str]):
    """
    Recursively generates a directory tree structure and counts image files.
    Populates `all_images_on_disk` with the names of all found image files.

    Args:
        path (str): The current directory path to process.
        prefix (str): The prefix string for tree indentation.
        output_lines (List[str]): A list to append formatted tree lines to.
        all_images_on_disk (Set[str]): A set to store the names of all found image files.
    """
    try:
        items = sorted(os.listdir(path))
    except (PermissionError, FileNotFoundError):
        output_lines.append(prefix + "└── [Access Denied or Not Found]")
        return

    image_counter: Dict[str, int] = defaultdict(int)
    non_image_files: List[str] = []

    for i, item in enumerate(items):
        full_path = os.path.join(path, item)
        is_last_item = (i == len(items) - 1)
        connector = "└── " if is_last_item else "├── "
        new_prefix = prefix + ("    " if is_last_item else "│   ")

        if os.path.isdir(full_path):
            output_lines.append(prefix + connector + item + "/")
            print_tree_and_count(full_path, new_prefix, output_lines, all_images_on_disk)
        else:
            if is_image_file(item):
                ext = get_extension(item)
                image_counter[ext] += 1
                all_images_on_disk.add(item) # Add just the filename, not full path
            else:
                non_image_files.append(item)

    # Append non-image files after directories and before image counts
    if non_image_files:
        for i, item in enumerate(non_image_files):
            is_last_non_image = (i == len(non_image_files) - 1 and not image_counter)
            connector_for_file = "└── " if is_last_non_image else "├── "
            output_lines.append(prefix + connector_for_file + item)

    if image_counter:
        for ext, count in sorted(image_counter.items()):
            # Adjust connector for image counts
            connector_for_count = "└── " if (not non_image_files and list(sorted(image_counter.keys()))[-1] == ext) else "├── "
            output_lines.append(prefix + connector_for_count + f"[{ext.upper()} files: {count}]")

def generate_tree_and_stats(folder_path: str, output_filename: str = "directory_tree_and_stats.md"):
    """
    Generates a markdown report containing the directory tree structure,
    image file counts, and statistics on image references.

    Args:
        folder_path (str): The path to the folder to be scanned.
        output_filename (str): The name of the markdown file to save the report to.
                               Defaults to "directory_tree_and_stats.md".
    """
    if not os.path.isdir(folder_path):
        print(f"Error: Invalid folder path: {folder_path}")
        return

    output_lines: List[str] = []
    output_lines.append(f"# 📁 Directory Tree and Image Statistics for `{os.path.basename(folder_path)}`\n")
    output_lines.append(os.path.basename(folder_path) + "/")

    all_images_on_disk: Set[str] = set()
    print_tree_and_count(folder_path, "", output_lines, all_images_on_disk)

    referenced_images: Set[str] = set()
    print("\nScanning for referenced images in caption files...")

    # Instantiate extractors once
    xlsx_extractor = XLSXReferenceExtractor()
    banglaview_xlsx_extractor = XLSXReferenceExtractor(has_header=False) # BanglaView has no header
    csv_extractor = CSVReferenceExtractor()
    json_extractor = JSONReferenceExtractor()
    txt_extractor = TXTReferenceExtractor()

    # Walk through the directory again to find and parse caption files
    for root, _, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            lower_file = file.lower()

            # Process general XLSX files containing "captioning" in their name.
            if lower_file.endswith(".xlsx") and "captioning" in lower_file:
                print(f"  - Extracting from XLSX: {file}")
                referenced_images.update(xlsx_extractor.extract(full_path))
            # Process CSV files containing "ban-cap" in their name.
            elif lower_file.endswith(".csv") and "ban-cap" in lower_file:
                print(f"  - Extracting from CSV: {file}")
                referenced_images.update(csv_extractor.extract(full_path))
            # Process the specific "banglaview_dataset.xlsx" file.
            elif lower_file == "banglaview_dataset.xlsx": # Specific file name for BanglaView
                print(f"  - Extracting from BanglaView XLSX: {file}")
                referenced_images.update(banglaview_xlsx_extractor.extract(full_path))
            # Process the BanglaLekhaImageCaptions dataset.
            elif lower_file.endswith(".json") and "caption" in lower_file:
                print(f"  - Extracting from JSON: {file}")
                referenced_images.update(json_extractor.extract(full_path))
            # Process the BNATURE dataset used for testing.
            elif lower_file == "caption.txt": # Specific file name for ground truth TXT
                print(f"  - Extracting from TXT: {file}")
                referenced_images.update(txt_extractor.extract(full_path))

    print("Finished scanning for referenced images.")

    # Normalize image names on disk for comparison (just filenames)
    normalized_images_on_disk = {os.path.basename(img) for img in all_images_on_disk}

    # Calculate statistics
    referenced_found = referenced_images.intersection(normalized_images_on_disk)
    referenced_missing = referenced_images.difference(normalized_images_on_disk)
    unused_images = normalized_images_on_disk.difference(referenced_images)

    # Append statistics to output
    output_lines.append("\n---\n")
    output_lines.append("## 📊 Image Statistics\n")
    output_lines.append(f"- 📷 **Total images found on disk:** `{len(normalized_images_on_disk)}`")
    output_lines.append(f"- 📝 **Total unique images referenced in caption files:** `{len(referenced_images)}`")
    output_lines.append(f"- ✅ **Referenced and found on disk:** `{len(referenced_found)}`")
    output_lines.append(f"- ❌ **Referenced in files but missing from disk:** `{len(referenced_missing)}`")
    output_lines.append(f"- 📦 **Unused images (on disk but not referenced):** `{len(unused_images)}`")
    output_lines.append("\n---\n")

    # Append lists of missing/unused images (sample)
    if referenced_missing:
        output_lines.append("### ❌ Missing Referenced Images (Sample):\n")
        for img_name in sorted(list(referenced_missing))[:10]:
            output_lines.append(f"- `{img_name}`")
        if len(referenced_missing) > 10:
            output_lines.append(f"- ... (and {len(referenced_missing) - 10} more)")

    if unused_images:
        output_lines.append("\n### 📦 Unused Images on Disk (Sample):\n")
        for img_name in sorted(list(unused_images))[:10]:
            output_lines.append(f"- `{img_name}`")
        if len(unused_images) > 10:
            output_lines.append(f"- ... (and {len(unused_images) - 10} more)")

    # Save the report to a markdown file
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))
        print(f"\n✅ Directory tree and stats saved to `{output_filename}`")
    except IOError as e:
        print(f"Error: Could not write to output file {output_filename}: {e}")

if __name__ == "__main__":
    print("--- Directory Tree & Image Analysis Script ---")
    print("This script generates a directory tree and analyzes image references within caption files.")

    folder_path_input = input("Enter the folder path to scan: ").strip()
    
    # Expand user home directory (e.g., ~) and resolve to an absolute path
    folder_path_to_scan = Path(folder_path_input).expanduser().resolve()

    generate_tree_and_stats(str(folder_path_to_scan))

    print("\nAnalysis complete.")