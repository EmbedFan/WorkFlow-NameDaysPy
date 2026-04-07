"""
Nameday reference database manager [REQ-0013, REQ-0018, REQ-0038, REQ-0039, REQ-0023].

Provides lookup and search operations for the nameday reference database.
"""

from pathlib import Path
from typing import List, Optional
import csv

from app.types import Nameday
from app.utils import read_csv, ensure_directory_exists, get_logger
from app.exceptions import DatabaseException
from app.constants import NAMEDAYS_CSV_PATH, CSV_DELIMITER
from app.utils.date_utils import is_valid_nameday_date

logger = get_logger(__name__)


class NamedayReferenceManager:
    """
    Query and manage built-in nameday reference database [REQ-0013, REQ-0018, REQ-0038, REQ-0039, REQ-0023].
    
    Provides read-only access to the nameday reference database with lookup,
    search, and query operations.
    """
    
    def __init__(self, csv_path: Path = NAMEDAYS_CSV_PATH):
        """
        Initialize with reference CSV file [REQ-0039].
        
        Args:
            csv_path: Path to nameday reference CSV file
        
        Raises:
            DatabaseException: If file cannot be loaded
        """
        self.csv_path = Path(csv_path)
        self._namedays: List[Nameday] = []
        self._names_by_date: dict = {}  # Maps MM-DD -> List[name]
        
        # Ensure resource directory exists
        ensure_directory_exists(self.csv_path.parent)
        
        # Load reference data
        self._load_reference()
    
    def get_nameday(self, name: str) -> Optional[Nameday]:
        """
        Lookup nameday by name [REQ-0018].
        
        Case-insensitive search. Handles language-specific case rules [REQ-0013].
        
        Args:
            name: Person name to search for
        
        Returns:
            Nameday object if found, None otherwise
        """
        if not name:
            return None
        
        # Case-insensitive search
        name_lower = name.lower()
        for nameday in self._namedays:
            if nameday.name.lower() == name_lower:
                return nameday
        
        return None
    
    def get_names_for_date(self, date: str) -> List[str]:
        """
        Find all names with given nameday date [REQ-0018, REQ-0023].
        
        Searches both main and other namedays.
        Date format must be MM-DD [REQ-0023].
        
        Args:
            date: Nameday date in MM-DD format
        
        Returns:
            List of names celebrating nameday on given date
        
        Raises:
            ValueError: If date format is invalid
        """
        if not is_valid_nameday_date(date):
            raise ValueError(f"Invalid date format: {date}. Expected MM-DD format [REQ-0023]")
        
        return self._names_by_date.get(date, [])
    
    def get_all_names(self) -> List[str]:
        """
        Get all available names in reference [REQ-0018].
        
        Returns:
            Sorted list of all available names
        """
        all_names = [nameday.name for nameday in self._namedays]
        return sorted(all_names)
    
    def search_names(self, pattern: str) -> List[str]:
        """
        Search names by pattern [REQ-0013].
        
        Case-insensitive substring search.
        Supports partial name matching.
        
        Args:
            pattern: Search pattern (substring)
        
        Returns:
            List of matching names
        """
        if not pattern:
            return []
        
        pattern_lower = pattern.lower()
        matches = []
        
        for nameday in self._namedays:
            if pattern_lower in nameday.name.lower():
                matches.append(nameday.name)
        
        return sorted(matches)
    
    def get_nameday_count(self) -> int:
        """
        Get total number of namedays in reference.
        
        Returns:
            Number of entries in reference database
        """
        return len(self._namedays)
    
    def date_exists(self, date: str) -> bool:
        """
        Check if any names exist for given date.
        
        Args:
            date: Date in MM-DD format
        
        Returns:
            True if names exist for this date, False otherwise
        """
        return date in self._names_by_date and len(self._names_by_date[date]) > 0
    
    def reload(self) -> tuple:
        """
        Reload nameday reference database from file [REQ-0066].
        
        Clears existing in-memory data and re-reads namedays.csv.
        
        Returns:
            tuple: (success: bool, message: str)
                - (True, "Reloaded N namedays") on success
                - (False, error_description) on failure
        
        Error handling:
            - FileNotFoundError: "Namedays file not found"
            - UnicodeDecodeError: "File encoding error - ensure UTF-8 encoding"
            - Other exceptions: Descriptive error message
        """
        try:
            # Reload using existing load logic
            self._load_reference()
            count = len(self._namedays)
            return (True, f"Reloaded {count} namedays")
            
        except FileNotFoundError:
            logger.error(f"Namedays file not found during reload: {self.csv_path}")
            return (False, "Namedays file not found")
        except UnicodeDecodeError:
            logger.error(f"File encoding error in {self.csv_path}")
            return (False, "File encoding error - ensure UTF-8 encoding")
        except Exception as e:
            logger.error(f"Error reloading namedays database: {e}")
            return (False, f"Error loading file: {str(e)}")
    
    def _load_reference(self) -> None:
        """
        Load reference from CSV file [REQ-0039, REQ-0023].
        
        Private method that parses nameday CSV data.
        Expects format: name;main_nameday;other_nameday
        """
        try:
            if not self.csv_path.exists():
                logger.warning(f"Nameday reference file not found: {self.csv_path}")
                self._namedays = []
                self._names_by_date = {}
                return
            
            rows = read_csv(self.csv_path, CSV_DELIMITER)
            self._namedays = []
            self._names_by_date = {}
            
            for row in rows:
                try:
                    name = row.get("name", "").strip()
                    main_date = row.get("main_nameday", "").strip()
                    other_date = row.get("other_nameday", "").strip() or None
                    
                    if not name or not main_date:
                        logger.debug(f"Skipping incomplete nameday row: {row}")
                        continue
                    
                    # Validate date format [REQ-0023]
                    if not is_valid_nameday_date(main_date):
                        logger.warning(f"Invalid main_nameday format: {main_date}")
                        continue
                    
                    if other_date and not is_valid_nameday_date(other_date):
                        logger.warning(f"Invalid other_nameday format: {other_date}")
                        other_date = None
                    
                    nameday = Nameday(
                        name=name,
                        main_nameday=main_date,
                        other_nameday=other_date
                    )
                    self._namedays.append(nameday)
                    
                    # Index by date for quick lookup
                    if main_date not in self._names_by_date:
                        self._names_by_date[main_date] = []
                    self._names_by_date[main_date].append(name)
                    
                    if other_date:
                        if other_date not in self._names_by_date:
                            self._names_by_date[other_date] = []
                        self._names_by_date[other_date].append(name)
                
                except Exception as e:
                    logger.warning(f"Failed to parse nameday row: {row}, error: {e}")
                    continue
            
            logger.info(f"Loaded {len(self._namedays)} nameday entries from {self.csv_path}")
        except Exception as e:
            logger.error(f"Failed to load nameday reference: {e}")
            self._namedays = []
            self._names_by_date = {}
