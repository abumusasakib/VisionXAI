# Caption Parsing Pipeline

The `CaptionParser` defines the interface for any class that extracts image-caption mappings from a data file.

## Imports

Necessary modules and classes are imported for file handling, data structures, and abstract base class definition.

```python
import csv
import zipfile
import xml.etree.ElementTree as ET
import os
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod

# Attempt to import cElementTree for faster XML parsing, fall back to ElementTree
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
```

## Abstract Base Class for Caption Parsers

The `CaptionParser` defines the interface for any class that extracts image-caption mappings from a data file.

```python
class CaptionParser(ABC):
    """
    Abstract Base Class for caption parsers.

    Defines the common interface for extracting image-caption mappings
    from different file formats (e.g., XLSX, CSV).
    """

    @abstractmethod
    def extract(self, file_path: str, images_path: str, validate_images: bool) -> Dict[str, List[str]]:
        """
        Abstract method to extract image-caption mappings from a given file.

        Args:
            file_path (str): The path to the data file (e.g., .xlsx, .csv).
            images_path (str): The base directory where image files are located.
            validate_images (bool): If True, checks if the image file exists on disk
                                    before including its captions in the output.

        Returns:
            Dict[str, List[str]]: A dictionary where keys are absolute image paths
                                  and values are lists of formatted captions.
        """
        pass
```

---

## XLSX Caption Parser

The `XLSXCaptionParser` class is responsible for extracting image and caption data from XLSX files. It handles the specific structure of Excel XML files, including shared strings and custom image name formats. It uses cElementTree if available and includes refined print-based progress indicators during row parsing.

```python
class XLSXCaptionParser(CaptionParser):
    """
    A concrete implementation of CaptionParser for XLSX files.

    It expects image names in the first column and captions in the second.
    Can handle files with or without a header row.
    Includes print-based progress indicators for row parsing.
    """

    def __init__(self, has_header: bool = True):
        """
        Initializes the XLSXCaptionParser.

        Args:
            has_header (bool, optional): Specifies if the XLSX file has a header row.
                                         If True, the first row is skipped during parsing. Defaults to True.
        """
        self.has_header = has_header

    def extract(self, xlsx_file: str, images_path: str = "", validate_images: bool = False) -> Dict[str, List[str]]:
        """
        Extracts image names and captions from an XLSX file.

        Args:
            xlsx_file (str): The path to the XLSX file.
            images_path (str, optional): Base directory where images are expected.
                                         If provided, image paths will be joined with this. Defaults to "".
            validate_images (bool, optional): If True, checks if the image file exists on disk.
                                              Only adds entries for existing images. Defaults to False.

        Returns:
            Dict[str, List[str]]: A dictionary where keys are image paths and values are lists of captions.
                                  Captions are formatted with `<start>` and `<end>` tokens.
        """
        caption_mapping: Dict[str, List[str]] = {}
        try:
            with zipfile.ZipFile(xlsx_file, "r") as xlsx:
                sheet_file = "xl/worksheets/sheet1.xml"
                shared_strings_file = "xl/sharedStrings.xml"

                # Define the namespace for OpenXML SpreadsheetML to correctly find elements.
                ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

                # Load shared strings; text content in XLSX is often stored in a shared strings table.
                shared_strings: List[str] = []
                if shared_strings_file in xlsx.namelist():
                    with xlsx.open(shared_strings_file) as f:
                        tree = ET.parse(f)
                        shared_strings = [
                            t.text
                            for t in tree.findall(f".//{ns}t")  # Find all 't' (text) elements within the namespace.
                            if t.text is not None
                        ]

                # If the main worksheet XML isn't found, return an empty mapping.
                if sheet_file not in xlsx.namelist():
                    print(f"Warning: Worksheet '{sheet_file}' not found in {xlsx_file}")
                    return caption_mapping

                with xlsx.open(sheet_file) as f:
                    tree = ET.parse(f)
                    rows = tree.findall(f".//{ns}row")  # Find all 'row' elements within the namespace.
                    # Determine the starting row based on whether a header is present.
                    start_row = 1 if self.has_header and len(rows) > 0 else 0
                    total_rows = len(rows[start_row:]) # Calculate total rows to process.

                    print(f"\n➡️  Parsing {os.path.basename(xlsx_file)} ({total_rows} rows)...")

                    for idx, row in enumerate(rows[start_row:], start=1):
                        # Print progress every 500 rows or at the last row, using carriage return for single line.
                        if idx % 500 == 0 or idx == total_rows:
                            print(f"\r  → Row {idx}/{total_rows}...", end="", flush=True)

                        # Filter for 'c' (cell) elements within the row, ensuring correct tag matching.
                        cells = [el for el in row if el.tag.endswith("c")]
                        if len(cells) < 2:  # Ensure there are at least two columns (image name and caption).
                            continue

                        def get_cell_value(cell: ET.Element) -> Optional[str]:
                            """Helper function to extract cell value, handling shared strings."""
                            cell_type = cell.get("t")  # 's' indicates shared string.
                            # Efficiently find the 'v' (value) element among cell children.
                            value_elem = next((v for v in cell if v.tag.endswith("v")), None)
                            if value_elem is not None and value_elem.text:
                                if cell_type == "s":
                                    try:
                                        idx = int(value_elem.text)
                                        return shared_strings[idx] if 0 <= idx < len(shared_strings) else None
                                    except (ValueError, IndexError):
                                        return None
                                return value_elem.text
                            return None

                        # Extract values from the first two cells (columns).
                        img_name_val = get_cell_value(cells[0])
                        caption_val = get_cell_value(cells[1])

                        if img_name_val:
                            # Clean and normalize image name (remove #index, replace *MG*).
                            if "#" in img_name_val:
                                img_name_val = img_name_val.split("#")[0]
                            img_name_val = img_name_val.replace("*MG*", "IMG_")
                            # Construct full image path.
                            img_path = os.path.join(images_path, img_name_val) if images_path else img_name_val

                            # Check for image existence only if validation is requested.
                            if not validate_images or Path(img_path).exists():
                                if caption_val:
                                    # Format caption with start/end tokens.
                                    formatted_caption = f"<start> {caption_val.strip()} <end>"
                                    # Add caption to the list for the corresponding image path.
                                    caption_mapping.setdefault(img_path, []).append(formatted_caption)

        except zipfile.BadZipFile:
            print(f"\nError: {xlsx_file} is not a valid zip file.")
        except Exception as e:
            print(f"\nAn error occurred while processing {xlsx_file}: {e}")

        return caption_mapping
```

---

## CSV Caption Parser

The `CSVCaptionParser` class handles the extraction of image and caption data from CSV files. It specifically looks for "caption\_id" and "bengali\_caption" columns and includes detailed print-based progress indicators as well.

```python
class CSVCaptionParser(CaptionParser):
    """
    A concrete implementation of CaptionParser for CSV files.

    It expects image names in a column named "caption_id" and
    captions in a column named "bengali_caption".
    Includes print-based progress indicators for row parsing.
    """

    def extract(self, csv_file_path: str, images_path: str = "", validate_images: bool = True) -> Dict[str, List[str]]:
        """
        Extracts image names and captions from a CSV file.

        Args:
            csv_file_path (str): The path to the CSV file.
            images_path (str, optional): Base directory where images are expected.
                                         If provided, image paths will be joined with this. Defaults to "".
            validate_images (bool, optional): If True, checks if the image file exists on disk.
                                              Only adds entries for existing images. Defaults to True.

        Returns:
            Dict[str, List[str]]: A dictionary where keys are image paths and values are lists of captions.
                                  Captions are formatted with `<start>` and `<end>` tokens.
        """
        caption_mapping: Dict[str, List[str]] = {}
        try:
            with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)  # Reads CSV into dictionary rows.

                rows = list(reader) # Load all rows into memory to get total count.
                total_rows = len(rows)

                csv_dir = os.path.dirname(os.path.abspath(csv_file_path))
                print(f"\n➡️  Parsing {os.path.basename(csv_file_path)} (folder: {csv_dir}, {total_rows} rows)...")
                for idx, row in enumerate(rows, start=1):
                    # Print progress every 500 rows or at the last row.
                    if idx % 500 == 0 or idx == total_rows:
                        print(f"\r  → Row {idx}/{total_rows}...", end='', flush=True)
                    
                    img_name = row.get("caption_id")
                    caption_bn = row.get("bengali_caption")

                    if img_name and caption_bn:
                        # Remove any '#index' suffix from the image name.
                        img_name = img_name.split("#")[0]
                        # Construct full image path.
                        img_path = os.path.join(images_path, img_name) if images_path else img_name

                        if validate_images and not Path(img_path).exists():
                            continue  # Skip if image validation is on and file not found.

                        # Add caption to the list for the corresponding image path.
                        caption_mapping.setdefault(img_path, []).append(f" <start> {caption_bn.strip()} <end> ")
        except FileNotFoundError:
            print(f"Error: CSV file not found at {csv_file_path}")
        except Exception as e:
            print(f"An error occurred while processing {csv_file_path}: {e}")

        return caption_mapping
```

## JSON Caption Parser

The `JSONCaptionParser` is a concrete implementation designed to parse specific JSON file structures, extracting filenames and their associated captions. It expects a list of objects, each with a 'filename' and a 'caption' (which is itself a list of strings).

```python
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
                        print(f"Warning: Skipping malformed JSON item in {file_path}: {item}")
                        continue

                    # Construct the full image path
                    img_name_from_json = item['filename'].strip()
                    img_name_abs = os.path.join(images_path, img_name_from_json)

                    # Ensure captions is a list, even if it's a single string
                    raw_captions = item['caption']
                    if not isinstance(raw_captions, list):
                        raw_captions = [raw_captions] # Convert single string to list

                    # Format captions (add leading/trailing spaces)
                    formatted_captions = [" " + str(caption).strip() + " " for caption in raw_captions if caption is not None]

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
```

---

## Data Collector

The `collect_all_caption_data` function orchestrates the process of finding and parsing caption files across a given directory structure. It intelligently determines the correct parser and image directory for different file types.

```python
def collect_all_caption_data(base_dir: str, validate_images: bool = True) -> Dict[str, List[str]]:
    """
    Walks through a base directory to find and extract caption data from XLSX and CSV files.
    It identifies different types of caption files based on their names and extensions
    and uses the appropriate parser.

    Args:
        base_dir (str): The root directory to start searching for files.
        validate_images (bool, optional): If True, validates image paths during extraction. Defaults to True.

    Returns:
        Dict[str, List[str]]: A consolidated dictionary of all found image-caption mappings.
    """
    all_captions: Dict[str, List[str]] = {}
    xlsx_parser = XLSXCaptionParser(has_header=True)
    csv_parser = CSVCaptionParser()
    banglaview_xlsx_parser = XLSXCaptionParser(has_header=False) # BanglaView has no header

    # Walk through the directory tree.
    print(f"🔍 Scanning directories in {base_dir}...")
    for root, dirs, files in os.walk(base_dir):
        # Indicate current directory being scanned.
        # This can be noisy for deep hierarchies, consider removing for very large datasets.
        # print(f"  📂 In directory: {root}")
        
        for file in files:
            lower_file = file.lower()
            file_path = os.path.join(root, file)
            captions: Dict[str, List[str]] = {}
            img_dir: str = ""

            # Process general XLSX files containing "captioning" in their name.
            if lower_file.endswith(".xlsx") and "captioning" in lower_file:
                img_dir = os.path.join(root, "image")
                if not os.path.exists(img_dir):
                    img_dir = root  # Fallback to the current directory if 'image' subfolder doesn't exist.
                # print(f"Parsing XLSX: {file_path}") # This print is inside the parser's extract method
                captions = xlsx_parser.extract(file_path, images_path=img_dir, validate_images=validate_images)

            # Process CSV files containing "ban-cap" in their name (e.g., Flickr 8k Bengali).
            elif lower_file.endswith(".csv") and "ban-cap" in lower_file:
                # Specific image directory structure for 'Flickr 8k Dataset'.
                img_dir = os.path.join(root, "Flickr 8k Dataset", "Images")
                if not os.path.exists(img_dir):
                    img_dir = base_dir  # Fallback to base_dir if the specific path isn't found.
                # print(f"Parsing CSV: {file_path}") # This print is inside the parser's extract method
                captions = csv_parser.extract(file_path, images_path=img_dir, validate_images=validate_images)

            # Process the specific "banglaview_dataset.xlsx" file.
            elif lower_file == "banglaview_dataset.xlsx":
                # Specific image directory structure for BanglaView.
                img_dir = os.path.join(base_dir, "flickr30k_images", "flickr30k_images")
                if not os.path.exists(img_dir):
                    print(f"Warning: BanglaView image directory not found at {img_dir}. Skipping.")
                    continue
                # print(f"Parsing BanglaView XLSX: {file_path}") # This print is inside the parser's extract method
                # BanglaView XLSX is known to have no header.
                captions = banglaview_xlsx_parser.extract(file_path, images_path=img_dir, validate_images=validate_images)
            else:
                continue # Skip files that don't match any known caption format.

            all_captions.update(captions)  # Merge new captions into the main dictionary.

    return all_captions
```

---

## Data Splitter

The `train_val_split` function provides a simple way to divide the collected image-caption data into training and validation sets, allowing for shuffling for better generalization.

```python
def train_val_split(caption_data: Dict[str, List[str]], train_size: float = 0.8, shuffle: bool = True) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """
    Splits image-caption data into training and validation sets.

    Args:
        caption_data (Dict[str, List[str]]): The full dictionary of image-caption mappings.
        train_size (float, optional): The proportion of data to allocate for training. Defaults to 0.8.
        shuffle (bool, optional): If True, shuffles the image paths before splitting. Defaults to True.

    Returns:
        Tuple[Dict[str, List[str]], Dict[str, List[str]]]: A tuple containing
        (training_data_dict, validation_data_dict).
    """
    all_images = list(caption_data.keys())

    if shuffle:
        random.shuffle(all_images)  # Randomize order of images.

    split_idx = int(len(all_images) * train_size)  # Calculate split index.
    train_data = {img: caption_data[img] for img in all_images[:split_idx]}
    val_data = {img: caption_data[img] for img in all_images[split_idx:]}

    return train_data, val_data
```

---

## Main Pipeline

This section demonstrates the complete workflow for using the defined classes and functions to process a dataset, from collecting data to splitting it and checking for missing files.

```python
# Collect, analyze, and split the caption data.

# 1. Collect all valid caption data (images that exist on disk)
print("Collecting all valid caption data...")
# Collect all captions, validating that the referenced image files exist on disk.
all_captions = collect_all_caption_data(dx, validate_images=True)

print(f"\n✅ Found {len(all_captions)} valid images with captions")
total_captions = sum(len(v) for v in all_captions.values())
print(f"📝 Total valid captions: {total_captions}\n")

# 2. Print a sample of the collected data
# Print a sample of the collected data for verification.
print("--- Sample of Collected Data ---")
for i, (img, captions) in enumerate(all_captions.items()):
    if i < 3: # Print details for the first 3 images
        print(f"Image: {img}")
        for j, caption in enumerate(captions[:2]): # Print up to 2 captions per image
            print(f"  Caption {j+1}: {caption}")
        print() # Add a newline for readability between image entries

# 3. Dataset split into training and validation sets
print("--- Splitting Dataset ---")
# Split the collected data into training and validation sets.
train_data, val_data = train_val_split(all_captions)
print(f"📊 Training samples: {len(train_data)}")
print(f"📊 Validation samples: {len(val_data)}")

# Preview only BanglaView entries
# Preview entries specific to the BanglaView dataset.
print("\n--- Previewing BanglaView Entries ---")
found_banglaview_sample = False
for img, caps in all_captions.items():
    if "flickr30k_images" in img.lower(): # Check for path indicating BanglaView.
        print(f"BanglaView Image: {img}")
        for c in caps:
            print(f"  Caption: {c}")
        found_banglaview_sample = True
        break # Only print one sample to keep output concise.
if not found_banglaview_sample:
    print("No BanglaView entries found in the collected data.")

# 4. Detect and report missing image entries
print("\n--- Detecting Missing Entries ---")
# Collect all entries from the files without validating image existence to identify potential missing files
all_entries = collect_all_caption_data(dx, validate_images=False)

# Find images that were referenced in files but not found on disk
missing_images = set(all_entries.keys()) - set(all_captions.keys())

print(f"\n⚠️ Missing images (referenced in Excel/CSV but not found on disk): {len(missing_images)}")

if missing_images:
    print("Sample of missing images:")
    for img in list(missing_images)[:5]: # Print up to 5 missing image paths
        print(f"  ❌ {img}")
else:
    print("🎉 No missing images found among referenced entries!")

```

## Ground Truth TXT Caption Parser

The `GroundTruthTXTCaptionParser` implements the `CaptionParser` for simple text files. It's designed to parse lines where the image filename and its caption are separated by three spaces.

```python
class GroundTruthTXTCaptionParser(CaptionParser):
    """
    A concrete implementation of CaptionParser for ground-truth TXT caption files.

    This parser expects each line in the text file to be formatted as:
    `image_filename   caption_text`
    where `image_filename` is the name of the image file (e.g., 'image.jpg')
    and `caption_text` is its corresponding caption, separated by exactly three spaces (`   `).
    """

    def extract(self, file_path: str, images_path: str = "", validate_images: bool = False) -> Dict[str, List[str]]:
        """
        Extracts image filenames and their associated captions from a plain text file.

        Args:
            file_path (str): The path to the TXT caption file.
            images_path (str, optional): The base directory where images referenced in the TXT
                                         file are located. Defaults to "".
            validate_images (bool, optional): If True, checks if the image file exists on disk
                                              before adding its captions. Defaults to False.

        Returns:
            Dict[str, List[str]]: A dictionary mapping absolute image paths to a list of their captions.
        """
        caption_mapping: Dict[str, List[str]] = {}
        print(f"➡️  Parsing TXT: {os.path.basename(file_path)}...")
        try:
            processed_lines = 0
            with open(file_path, "r", encoding="utf-8") as file:
                for idx, line in enumerate(file, 1):
                    line = line.strip()
                    if not line:
                        continue  # Skip empty lines

                    # Log progress for large files
                    if idx % 1000 == 0:
                        print(f"\r  → Processing line {idx}...", end="", flush=True)

                    # Split by exactly three spaces. Using `maxsplit=1` ensures only the first
                    # occurrence of "   " splits the line into two parts.
                    parts = line.split("   ", 1)  # 3 spaces
                    if len(parts) < 2:
                        print(f"Warning: Skipping malformed line {idx} in {file_path}: '{line}' (expected 'filename   caption')")
                        continue  # Skip malformed lines

                    img_name_from_file = parts[0].strip()
                    raw_caption = parts[1].strip()

                    # Construct the full image path
                    img_path = os.path.join(images_path, img_name_from_file) if images_path else img_name_from_file

                    # Validate image existence if requested
                    if not validate_images or Path(img_path).exists():
                        caption_mapping.setdefault(img_path, []).append(raw_caption)
                        processed_lines += 1
                    # else:
                        # print(f"Debug: Image '{img_path}' not found on disk. Skipped during validation.")
                
                print(f"\r  → Finished parsing {os.path.basename(file_path)}. Total valid entries: {processed_lines}.", flush=True)

        except FileNotFoundError:
            print(f"\nError: TXT file not found at {file_path}")
        except Exception as e:
            # Print a newline to prevent overwriting the progress message
            print(f"\n[TXT] An unexpected error occurred while reading {file_path}: {e}")

        return caption_mapping
```

## Ground Truth TXT Caption Parser Usage

This section uses the `GroundTruthTXTCaptionParser` to extract captions from a `.txt` file, assuming a specific directory structure for the dataset.

```python
# Main loop to process test images
dataset_directory = "/data/test/BNATURE/"
test_image_directory = dataset_directory+"Pictures"
test_image_filenames = os.listdir(test_image_directory)

# --- Ground Truth TXT Caption Parser Usage ---
print("--- GroundTruthTXTCaptionParser Started---")

# Ensure the test directory exists
if not os.path.isdir(dataset_directory):
    print(f"\nError: Test dataset directory not found at '{dataset_directory}'.")
    print("Please update 'dataset_directory' to a valid path containing 'caption/caption.txt' and 'Pictures'.")

# Initialize the GroundTruthTXTCaptionParser
txt_parser = GroundTruthTXTCaptionParser()

# Define the paths to the caption file and the corresponding image directory
captions_file_path = os.path.join(dataset_directory, "caption", "caption.txt")
images_directory_path = os.path.join(dataset_directory, "Pictures")

# Extract ground-truth captions
# Setting `validate_images=True` will ensure that only captions for images
# that actually exist on disk are included in the `ground_truth_captions` dictionary.
print(f"\nAttempting to extract captions from: {captions_file_path}")
print(f"Looking for images in: {images_directory_path}")
ground_truth_captions = txt_parser.extract(
    file_path=captions_file_path,
    images_path=images_directory_path,
    validate_images=True
)

# Display a sample of parsed captions to verify extraction
print("\n--- Sample of Parsed Ground Truth Captions ---")
if ground_truth_captions:
    for i, (img_path, caps) in enumerate(ground_truth_captions.items()):
        print(f"Image Path: {img_path}")
        for j, caption in enumerate(caps):
            print(f"  Caption {j+1}: {caption}")
        print() # Add a blank line for readability between entries
        if i >= 2: # Display only the first 3 entries for brevity
            break
else:
    print("No captions were extracted. Please check file paths and format.")

print("--- GroundTruthTXTCaptionParser complete ---")
```
