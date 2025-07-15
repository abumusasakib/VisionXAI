# VisionXAI Utilities

This repository contains a collection of Python utilities designed to assist with various data processing and management tasks for computer vision and AI projects. Each utility is organized in its own directory for clarity and modularity.

## Utilities Overview

### 1. clipboard_whitespace_clean

- **File:** `clipboard_clean.py`
- **Description:**
  - Cleans up whitespace from clipboard contents. Useful for quickly sanitizing copied text data.

### 2. dataset_directory_tree

- **File:** `dataset_directory_tree.py`
- **Description:**
  - Parses datasets and provides tools for analyzing dataset structures. Includes utilities for visualizing and documenting directory trees.
- **Additional:**
  - `caption parsing pipeline.md`: Documentation of the caption parsing pipeline.

### 3. dataset_integrity_check

- **File:** `dataset_integrity_check.py`
- **Description:**
  - Checks the integrity of the BanglaLekhaImageCaptions dataset, including file existence, format validation, and optional caption parsing. Includes submodule for custom caption parsers.
- **Additional:**
  - `caption_parsers/`: Contains custom caption parser modules.

### 4. check_tensorflow_weights

- **File:** `check_tensorflow_weights.py`
- **Description:**
  - Utility to inspect and validate TensorFlow model weights for compatibility and integrity.

### 5. filter_images

- **File:** `filter_images.py`
- **Description:**
  - Filters images in a directory based on specified criteria (e.g., size, format, or custom rules).

### 6. save_vocab_pickle

- **File:** `save_vocab_pickle.py`
- **Description:**
  - Saves vocabulary or other Python objects as pickle files for later use in machine learning workflows.

---

## Usage

Each utility can be run independently. Navigate to the respective directory and execute the Python script. For example:

```powershell
cd clipboard_whitespace_clean
python clipboard_clean.py
```

Refer to the source code of each script for specific usage instructions and configurable options.

## Requirements

- Recommended Python version: Python 3.8.5
- Additional dependencies may be required for specific utilities. Please check the script headers or use `pip install -r requirements.txt` if available.

## License

This project is provided for educational and research purposes.
