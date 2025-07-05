import os
import zipfile
import xml.etree.ElementTree as ET # Standard ElementTree is used for XML parsing
import csv
from pathlib import Path
from collections import defaultdict
from typing import Set, List, Dict, Optional

# --- Constants ---
# Set of common image file extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}

# --- Helper Functions ---

def is_image_file(filename: str) -> bool:
    """
    Checks if a given filename has a recognized image extension.

    Args:
        filename (str): The name of the file.

    Returns:
        bool: True if the file has an image extension, False otherwise.
    """
    return os.path.splitext(filename)[1].lower() in IMAGE_EXTENSIONS

def get_extension(filename: str) -> str:
    """
    Extracts and returns the lowercase file extension from a filename.

    Args:
        filename (str): The name of the file.

    Returns:
        str: The lowercase file extension (e.g., ".jpg", ".txt").
    """
    return os.path.splitext(filename)[1].lower()

def extract_referenced_images_from_xlsx(filepath: str) -> Set[str]:
    """
    Extracts unique image names referenced in the first column of an XLSX file.
    Handles shared strings and specific image name formatting (e.g., stripping "#" and replacing "*MG*").

    Args:
        filepath (str): The path to the XLSX file.

    Returns:
        Set[str]: A set of normalized image names referenced in the XLSX file.
    """
    referenced_images = set()
    try:
        with zipfile.ZipFile(filepath, "r") as xlsx:
            sheet_file = "xl/worksheets/sheet1.xml"
            shared_strings_file = "xl/sharedStrings.xml"

            ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
            shared_strings: List[str] = []

            # Load shared strings from the XML part if available
            if shared_strings_file in xlsx.namelist():
                with xlsx.open(shared_strings_file) as f:
                    tree = ET.parse(f)
                    shared_strings = [
                        t.text for t in tree.findall(f".//{ns}t") if t.text is not None
                    ]

            if sheet_file not in xlsx.namelist():
                print(f"Warning: Worksheet '{sheet_file}' not found in {filepath}")
                return referenced_images

            # Parse the main worksheet XML to find image names
            with xlsx.open(sheet_file) as f:
                tree = ET.parse(f)
                rows = tree.findall(f".//{ns}row")
                # Assume a header if there's more than one row. Skip first row if header exists.
                start_row = 1 if len(rows) > 1 else 0

                for row in rows[start_row:]:
                    # Filter for 'c' (cell) elements within the row
                    cells = [el for el in row if el.tag.endswith("c")]
                    if not cells: # Skip if no cells in row
                        continue

                    cell = cells[0] # Consider only the first cell (column A)
                    cell_type = cell.get("t") # 's' indicates a shared string reference
                    value_elem = next((v for v in cell if v.tag.endswith("v")), None) # Find 'v' (value) element

                    if value_elem is not None and value_elem.text:
                        val: Optional[str] = None
                        if cell_type == "s":
                            try:
                                idx = int(value_elem.text)
                                val = shared_strings[idx] if 0 <= idx < len(shared_strings) else None
                            except (ValueError, IndexError):
                                pass
                        else:
                            val = value_elem.text

                        if val:
                            # Clean and normalize image name (remove #index, replace *MG*)
                            img_name = val.split("#")[0].replace("*MG*", "IMG_").strip()
                            referenced_images.add(img_name)
    except zipfile.BadZipFile:
        print(f"[XLSX] Error: {filepath} is not a valid zip file (corrupted XLSX).")
    except Exception as e:
        print(f"[XLSX] An error occurred while reading {filepath}: {e}")
    return referenced_images

def extract_referenced_images_from_csv(filepath: str) -> Set[str]:
    """
    Extracts unique image names referenced in the "caption_id" column of a CSV file.

    Args:
        filepath (str): The path to the CSV file.

    Returns:
        Set[str]: A set of normalized image names referenced in the CSV file.
    """
    referenced_images = set()
    try:
        with open(filepath, encoding="utf-8", newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                val = row.get("caption_id", "")
                if val:
                    # Clean and normalize image name (remove #index)
                    img_name = val.split("#")[0].strip()
                    referenced_images.add(img_name)
    except FileNotFoundError:
        print(f"[CSV] Error: File not found at {filepath}")
    except Exception as e:
        print(f"[CSV] An error occurred while reading {filepath}: {e}")
    return referenced_images

def print_tree_and_count(
    path: str,
    prefix: str,
    output_lines: List[str],
    all_images_on_disk: Set[str]
):
    """
    Recursively generates a directory tree, counts image files by extension,
    and collects all image filenames found on disk. The results are appended
    to `output_lines` and `all_images_on_disk` in place.

    Args:
        path (str): The current directory path to process.
        prefix (str): The string prefix for current tree level (for indentation).
        output_lines (List[str]): A list to which formatted tree lines are appended.
        all_images_on_disk (Set[str]): A set to which all found image filenames are added.
    """
    try:
        items = sorted(os.listdir(path))
    except PermissionError:
        output_lines.append(prefix + "└── [Permission Denied]")
        return
    except FileNotFoundError:
        output_lines.append(prefix + "└── [Not Found]")
        return

    image_counter: Dict[str, int] = defaultdict(int)
    non_image_files: List[str] = [] # To list other files explicitly

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
                all_images_on_disk.add(item) # Add the basename of the image file
            else:
                # Collect non-image files to print them at the end of the directory listing
                non_image_files.append(item)

    # Print non-image files for the current directory
    for i, item in enumerate(non_image_files):
        is_last_non_image = (i == len(non_image_files) - 1 and not image_counter)
        connector = "└── " if is_last_non_image else "├── "
        output_lines.append(prefix + connector + item)

    # Print image counts for the current directory
    if image_counter:
        for ext, count in sorted(image_counter.items()):
            # If there were non_image_files, and this is the last entry, use '└── ' for the last image type summary
            if non_image_files and not is_last_item: # Check for the 'is_last_item' for current directory's last file
                 # This logic for connector for image counts needs adjustment to be consistent.
                 # Let's simplify: image counts are always listed after individual files.
                 # The '└── ' should apply to the very last line printed for this directory's contents.
                pass
            output_lines.append(prefix + f"[{ext} files: {count}]")


# --- Main Logic ---

def generate_tree_and_stats(folder_path: str, output_filename: str = "directory_tree_and_stats.md"):
    """
    Generates a detailed directory tree for the given folder, including file counts
    for image types, and compares images found on disk with those referenced in
    specific XLSX and CSV caption files. Outputs the results to a Markdown file.

    Args:
        folder_path (str): The root path of the folder to scan.
        output_filename (str, optional): The name of the output Markdown file.
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
    # Walk through the directory again to find caption files
    for root, _, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            lower_file = file.lower()
            if lower_file.endswith(".xlsx") and "captioning" in lower_file:
                print(f"  - Extracting from XLSX: {file} (in {root})")
                referenced_images.update(extract_referenced_images_from_xlsx(full_path))
            elif lower_file.endswith(".csv") and "ban-cap" in lower_file:
                print(f"  - Extracting from CSV: {file} (in {root})")
                referenced_images.update(extract_referenced_images_from_csv(full_path))
            elif lower_file == "banglaview_dataset.xlsx":
                print(f"  - Extracting from BanglaView XLSX: {file} (in {root})")
                referenced_images.update(extract_referenced_images_from_xlsx(full_path))
    print("Finished scanning for referenced images.")

    # Normalize image names on disk by taking only their basenames for comparison
    normalized_images_on_disk = {os.path.basename(img) for img in all_images_on_disk}

    # Perform set operations for statistics
    referenced_found = referenced_images.intersection(normalized_images_on_disk)
    referenced_missing = referenced_images.difference(normalized_images_on_disk)
    unused_images = normalized_images_on_disk.difference(referenced_images)

    output_lines.append("\n---\n") # Separator
    output_lines.append("## 📊 Image Statistics\n")
    output_lines.append(f"- 📷 **Total images found on disk:** `{len(normalized_images_on_disk)}`")
    output_lines.append(f"- 📝 **Total unique images referenced in .xlsx/.csv files:** `{len(referenced_images)}`")
    output_lines.append(f"- ✅ **Referenced and found on disk:** `{len(referenced_found)}`")
    output_lines.append(f"- ❌ **Referenced in files but missing from disk:** `{len(referenced_missing)}`")
    output_lines.append(f"- 📦 **Unused images (on disk but not referenced in files):** `{len(unused_images)}`")
    output_lines.append("\n---\n")

    # Optionally list missing and unused images
    if referenced_missing:
        output_lines.append("### ❌ Missing Referenced Images (Sample):\n")
        # Sort for consistent output
        for img_name in sorted(list(referenced_missing))[:10]: # Limit sample to 10
            output_lines.append(f"- `{img_name}`")
        if len(referenced_missing) > 10:
            output_lines.append(f"- ... (and {len(referenced_missing) - 10} more)")

    if unused_images:
        output_lines.append("\n### 📦 Unused Images on Disk (Sample):\n")
        # Sort for consistent output
        for img_name in sorted(list(unused_images))[:10]: # Limit sample to 10
            output_lines.append(f"- `{img_name}`")
        if len(unused_images) > 10:
            output_lines.append(f"- ... (and {len(unused_images) - 10} more)")


    # Write the collected lines to the output file
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))
        print(f"\n✅ Directory tree and stats saved to `{output_filename}`")
    except IOError as e:
        print(f"Error: Could not write to output file {output_filename}: {e}")

# --- Main Execution ---

if __name__ == "__main__":
    print("--- Directory Tree & Image Analysis Script ---")
    print("This script generates a directory tree and analyzes image references.")
    folder_path_input = input("Enter the folder path to scan: ").strip()

    # Normalize path: expand user home directory and resolve to an absolute path
    folder_path_to_scan = Path(folder_path_input).expanduser().resolve()

    generate_tree_and_stats(str(folder_path_to_scan))
    print("\nAnalysis complete.")