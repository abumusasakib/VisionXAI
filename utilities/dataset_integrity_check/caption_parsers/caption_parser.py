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

