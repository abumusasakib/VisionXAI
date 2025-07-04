import os
import zipfile
import xml.etree.ElementTree as ET
import csv
from pathlib import Path
from collections import defaultdict

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}

# Helpers
def is_image_file(filename):
    return os.path.splitext(filename)[1].lower() in IMAGE_EXTENSIONS

def get_extension(filename):
    return os.path.splitext(filename)[1].lower()

def extract_referenced_images_from_xlsx(filepath):
    referenced_images = set()
    try:
        with zipfile.ZipFile(filepath, "r") as xlsx:
            sheet_file = "xl/worksheets/sheet1.xml"
            shared_strings_file = "xl/sharedStrings.xml"

            # Load shared strings
            shared_strings = []
            if shared_strings_file in xlsx.namelist():
                with xlsx.open(shared_strings_file) as f:
                    tree = ET.parse(f)
                    shared_strings = [
                        t.text for t in tree.findall(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")
                    ]

            if sheet_file not in xlsx.namelist():
                return referenced_images

            with xlsx.open(sheet_file) as f:
                tree = ET.parse(f)
                rows = tree.findall(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row")[1:]

                for row in rows:
                    cells = row.findall(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c")
                    if len(cells) < 1:
                        continue

                    cell = cells[0]
                    cell_type = cell.get("t")
                    value_elem = cell.find(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v")

                    if value_elem is not None:
                        if cell_type == "s":
                            idx = int(value_elem.text)
                            val = shared_strings[idx] if 0 <= idx < len(shared_strings) else ""
                        else:
                            val = value_elem.text
                        if val:
                            img_name = val.split("#")[0].replace("*MG*", "IMG_").strip()
                            referenced_images.add(img_name)
    except Exception as e:
        print(f"[XLSX] Error reading {filepath}: {e}")
    return referenced_images

def extract_referenced_images_from_csv(filepath):
    referenced_images = set()
    try:
        with open(filepath, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                val = row.get("caption_id", "")
                if val:
                    img_name = val.split("#")[0].strip()
                    referenced_images.add(img_name)
    except Exception as e:
        print(f"[CSV] Error reading {filepath}: {e}")
    return referenced_images

def print_tree_and_count(path, prefix="", output_lines=None, all_images=None):
    try:
        items = sorted(os.listdir(path))
    except PermissionError:
        output_lines.append(prefix + "└── [Permission Denied]")
        return

    image_counter = defaultdict(int)
    other_files = []

    for item in items:
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            connector = "└── " if item == items[-1] else "├── "
            output_lines.append(prefix + connector + item + "/")
            new_prefix = prefix + ("    " if item == items[-1] else "│   ")
            print_tree_and_count(full_path, new_prefix, output_lines, all_images)
        else:
            if is_image_file(item):
                ext = get_extension(item)
                image_counter[ext] += 1
                all_images.add(item)
            else:
                connector = "└── " if item == items[-1] else "├── "
                output_lines.append(prefix + connector + item)

    if image_counter:
        for ext, count in sorted(image_counter.items()):
            output_lines.append(prefix + f"[{ext} files: {count}]")

def generate_tree_and_stats(folder_path, output_filename="directory_tree.md"):
    if not os.path.isdir(folder_path):
        print(f"Invalid folder path: {folder_path}")
        return

    output_lines = []
    output_lines.append(f"# 📁 Directory Tree of `{os.path.basename(folder_path)}`\n")
    output_lines.append(os.path.basename(folder_path) + "/")

    all_images_on_disk = set()
    print_tree_and_count(folder_path, "", output_lines, all_images_on_disk)

    referenced_images = set()
    for root, _, files in os.walk(folder_path):
        for file in files:
            ext = file.lower()
            full_path = os.path.join(root, file)
            if ext.endswith(".xlsx") and "captioning" in ext:
                referenced_images.update(extract_referenced_images_from_xlsx(full_path))
            elif ext.endswith(".csv") and "ban-cap" in ext:
                referenced_images.update(extract_referenced_images_from_csv(full_path))

    # Normalize all_images_on_disk by name only
    normalized_images = {os.path.basename(img) for img in all_images_on_disk}

    referenced_found = referenced_images & normalized_images
    referenced_missing = referenced_images - normalized_images
    unused_images = normalized_images - referenced_images

    output_lines.append("\n---")
    output_lines.append(f"📷 Total images found on disk: {len(normalized_images)}")
    output_lines.append(f"📝 Total images referenced in .xlsx/.csv: {len(referenced_images)}")
    output_lines.append(f"✅ Referenced & found: {len(referenced_found)}")
    output_lines.append(f"❌ Referenced but missing: {len(referenced_missing)}")
    output_lines.append(f"📦 Unused images (not referenced): {len(unused_images)}")
    output_lines.append("---")

    # Save report
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print(f"\n✅ Directory tree and stats saved to `{output_filename}`")


# === Example usage ===
folder_path = input("Enter the folder path to scan: ").strip()
generate_tree_and_stats(folder_path)
