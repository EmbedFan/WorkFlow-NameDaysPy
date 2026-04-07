"""
Utility module for file operations and path management.

Handles CSV file I/O, JSON operations, and file system utilities.
"""

import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.exceptions import FileOperationException
from app.constants import CSV_ENCODING, CSV_DELIMITER


def ensure_directory_exists(path: Path) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to ensure exists
    
    Raises:
        FileOperationException: If directory creation fails
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise FileOperationException(f"Failed to create directory: {path}", str(path)) from e


def read_csv(file_path: Path, delimiter: str = CSV_DELIMITER) -> List[Dict[str, str]]:
    """
    Read CSV file and return list of dictionaries.
    
    Args:
        file_path: Path to CSV file
        delimiter: CSV delimiter character (default: semicolon)
    
    Returns:
        List of dictionaries representing CSV rows
    
    Raises:
        FileOperationException: If file reading fails
    """
    try:
        if not file_path.exists():
            return []
        
        rows = []
        with open(file_path, mode='r', encoding=CSV_ENCODING, newline='') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            if reader.fieldnames is None:
                return []
            for row in reader:
                rows.append(row)
        return rows
    except Exception as e:
        raise FileOperationException(f"Failed to read CSV file: {file_path}", str(file_path)) from e


def write_csv(
    file_path: Path,
    rows: List[Dict[str, str]],
    fieldnames: List[str],
    delimiter: str = CSV_DELIMITER
) -> None:
    """
    Write list of dictionaries to CSV file.
    
    Args:
        file_path: Path to CSV file
        rows: List of dictionaries to write
        fieldnames: List of field names (column headers)
        delimiter: CSV delimiter character (default: semicolon)
    
    Raises:
        FileOperationException: If file writing fails
    """
    try:
        ensure_directory_exists(file_path.parent)
        
        with open(file_path, mode='w', encoding=CSV_ENCODING, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
            writer.writeheader()
            writer.writerows(rows)
    except Exception as e:
        raise FileOperationException(f"Failed to write CSV file: {file_path}", str(file_path)) from e


def read_json(file_path: Path) -> Dict[str, Any]:
    """
    Read JSON file and return dictionary.
    
    Args:
        file_path: Path to JSON file
    
    Returns:
        Dictionary from JSON file
    
    Raises:
        FileOperationException: If file reading fails
    """
    try:
        if not file_path.exists():
            return {}
        
        with open(file_path, mode='r', encoding=CSV_ENCODING) as f:
            return json.load(f)
    except Exception as e:
        raise FileOperationException(f"Failed to read JSON file: {file_path}", str(file_path)) from e


def write_json(file_path: Path, data: Dict[str, Any], indent: int = 2) -> None:
    """
    Write dictionary to JSON file.
    
    Args:
        file_path: Path to JSON file
        data: Dictionary to write
        indent: JSON indentation level
    
    Raises:
        FileOperationException: If file writing fails
    """
    try:
        ensure_directory_exists(file_path.parent)
        
        with open(file_path, mode='w', encoding=CSV_ENCODING) as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    except Exception as e:
        raise FileOperationException(f"Failed to write JSON file: {file_path}", str(file_path)) from e


def file_exists(file_path: Path) -> bool:
    """
    Check if file exists.
    
    Args:
        file_path: Path to check
    
    Returns:
        True if file exists, False otherwise
    """
    try:
        return file_path.exists() and file_path.is_file()
    except Exception:
        return False


def get_file_size(file_path: Path) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to file
    
    Returns:
        File size in bytes, or -1 if file doesn't exist
    """
    try:
        if file_path.exists():
            return file_path.stat().st_size
        return -1
    except Exception:
        return -1


def delete_file(file_path: Path) -> bool:
    """
    Delete a file.
    
    Args:
        file_path: Path to file to delete
    
    Returns:
        True if deletion successful, False otherwise
    """
    try:
        if file_path.exists():
            file_path.unlink()
        return True
    except Exception:
        return False


def backup_file(file_path: Path, suffix: str = ".bak") -> Optional[Path]:
    """
    Create a backup copy of a file.
    
    Args:
        file_path: Path to file to backup
        suffix: Suffix to add to backup filename
    
    Returns:
        Path to backup file, or None if creation failed
    """
    try:
        if not file_path.exists():
            return None
        
        backup_path = file_path.parent / f"{file_path.name}{suffix}"
        file_path.replace(backup_path)
        return backup_path
    except Exception:
        return None
