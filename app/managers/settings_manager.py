"""
Settings manager for application configuration [REQ-0014, REQ-0026, REQ-0028, REQ-0055].

Provides persistent settings management with JSON file storage.
"""

from pathlib import Path
from typing import Any, Optional, Tuple

from app.types import Settings
from app.utils import read_json, write_json, ensure_directory_exists, get_logger
from app.exceptions import ConfigurationException
from app.constants import CONFIG_JSON_PATH, DEFAULT_CHECK_INTERVAL_MINUTES, DEFAULT_LANGUAGE
from app.constants import DEFAULT_AUTO_LAUNCH, DEFAULT_NOTIFICATIONS_ENABLED

logger = get_logger(__name__)


class SettingsManager:
    """
    Manage application settings with persistence [REQ-0014, REQ-0026, REQ-0028, REQ-0055].
    
    Settings are persisted to JSON file [REQ-0055].
    Default settings are applied if config file is missing or incomplete [REQ-0028].
    """
    
    def __init__(self, config_path: Path = CONFIG_JSON_PATH):
        """
        Initialize settings manager with config file path [REQ-0026].
        
        Args:
            config_path: Path to configuration JSON file
        """
        self.config_path = Path(config_path)
        ensure_directory_exists(self.config_path.parent)
        
        # Load settings (with defaults if needed)
        self._settings = self.load_settings()
    
    def load_settings(self) -> Settings:
        """
        Load settings from config file [REQ-0026].
        
        Applies default values for missing settings [REQ-0028].
        
        Returns:
            Settings object with loaded or default values
        """
        try:
            if self.config_path.exists():
                config_data = read_json(self.config_path)
                return Settings.from_dict(config_data)
            else:
                # Create defaults and save
                self._create_default_config()
                return Settings()
        except Exception as e:
            logger.warning(f"Failed to load settings: {e}. Using defaults.")
            return Settings()
    
    def save_settings(self, settings: Optional[Settings] = None) -> None:
        """
        Save settings to config file [REQ-0026].
        
        Args:
            settings: Settings object to save (uses current if None)
        
        Raises:
            ConfigurationException: If save operation fails
        """
        try:
            if settings is None:
                settings = self._settings
            else:
                self._settings = settings
            
            ensure_directory_exists(self.config_path.parent)
            write_json(self.config_path, settings.to_dict())
            logger.info(f"Settings saved to {self.config_path}")
        except Exception as e:
            raise ConfigurationException(f"Failed to save settings: {e}") from e
    
    def get_setting(self, key: str) -> Any:
        """
        Get individual setting value [REQ-0026].
        
        Args:
            key: Setting key name
        
        Returns:
            Setting value or None if not found
        """
        return getattr(self._settings, key, None)
    
    def set_setting(self, key: str, value: Any) -> None:
        """
        Update individual setting and save [REQ-0026].
        
        Args:
            key: Setting key name
            value: New value
        
        Raises:
            ConfigurationException: If invalid key or save fails
        """
        if not hasattr(self._settings, key):
            raise ConfigurationException(f"Unknown setting key: {key}")
        
        setattr(self._settings, key, value)
        self.save_settings()
        logger.info(f"Setting updated: {key} = {value}")
    
    def reset_to_defaults(self) -> None:
        """
        Reset all settings to defaults [REQ-0028].
        
        Useful for corrupted config recovery.
        """
        self._settings = Settings()
        self.save_settings()
        logger.info("Settings reset to defaults")
    
    def get_settings(self) -> Settings:
        """
        Get current settings object.
        
        Returns:
            Settings object
        """
        return self._settings
    
    @property
    def language(self) -> str:
        """
        Get user's preferred language [REQ-0045, REQ-0046].
        
        Returns:
            Language code ("en" or "hu")
        """
        from app.constants import SUPPORTED_LANGUAGES
        
        language = getattr(self._settings, "language", "en")
        # Validate against supported languages
        if language not in SUPPORTED_LANGUAGES:
            language = "en"
        return language
    
    def update_settings(self, **kwargs) -> None:
        """
        Update multiple settings at once.
        
        Args:
            **kwargs: Key=value pairs to update
        
        Raises:
            ConfigurationException: If any key is invalid
        """
        for key, value in kwargs.items():
            if not hasattr(self._settings, key):
                raise ConfigurationException(f"Unknown setting key: {key}")
            setattr(self._settings, key, value)
        
        self.save_settings()
        logger.info(f"Settings updated: {list(kwargs.keys())}")
    
    def is_valid(self) -> bool:
        """
        Check if current settings are valid.
        
        Returns:
            True if settings pass validation, False otherwise
        """
        # Validate check interval
        from app.constants import MIN_CHECK_INTERVAL, MAX_CHECK_INTERVAL
        from app.constants import SUPPORTED_LANGUAGES
        
        if not (MIN_CHECK_INTERVAL <= self._settings.check_interval <= MAX_CHECK_INTERVAL):
            return False
        
        # Validate language
        if self._settings.language not in SUPPORTED_LANGUAGES:
            return False
        
        return True
    
    def validate_and_fix(self) -> bool:
        """
        Validate settings and attempt to fix invalid values.
        
        Returns:
            True if settings are now valid, False if validation failed beyond repair
        """
        from app.constants import MIN_CHECK_INTERVAL, MAX_CHECK_INTERVAL
        from app.constants import SUPPORTED_LANGUAGES
        
        fixed = False
        
        # Validate and fix check interval
        if not (MIN_CHECK_INTERVAL <= self._settings.check_interval <= MAX_CHECK_INTERVAL):
            logger.warning(f"Invalid check_interval: {self._settings.check_interval}. Resetting to default.")
            self._settings.check_interval = DEFAULT_CHECK_INTERVAL_MINUTES
            fixed = True
        
        # Validate and fix language
        if self._settings.language not in SUPPORTED_LANGUAGES:
            logger.warning(f"Invalid language: {self._settings.language}. Resetting to default.")
            self._settings.language = DEFAULT_LANGUAGE
            fixed = True
        
        if fixed:
            self.save_settings()
        
        return self.is_valid()
    
    def _create_default_config(self) -> None:
        """
        Create default config file [REQ-0028].
        
        Creates a new config file with default settings.
        """
        try:
            ensure_directory_exists(self.config_path.parent)
            default_settings = Settings(
                check_interval=DEFAULT_CHECK_INTERVAL_MINUTES,
                auto_launch=DEFAULT_AUTO_LAUNCH,
                language=DEFAULT_LANGUAGE,
                notifications_enabled=DEFAULT_NOTIFICATIONS_ENABLED
            )
            write_json(self.config_path, default_settings.to_dict())
            logger.info(f"Default configuration created at {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to create default config: {e}")
    
    # ===== Column Width Management Methods [REQ-0056, REQ-0057, REQ-0058, REQ-0059, REQ-0060] =====
    
    def get_column_width(self, column_name: str) -> int:
        """
        Get saved column width from config [REQ-0060].
        
        Args:
            column_name: Name of column (e.g., "Name", "Email")
        
        Returns:
            Width in pixels, or default if not found (minimum 50px)
        """
        try:
            config_data = read_json(self.config_path) if self.config_path.exists() else {}
            widths = config_data.get("database_editor", {}).get("column_widths", {})
            width = widths.get(column_name, 0)
            return max(width, 50) if width > 0 else 0
        except Exception as e:
            logger.warning(f"Failed to get column width for {column_name}: {e}")
            return 0
    
    def set_column_width(self, column_name: str, width: int) -> None:
        """
        Store one column width [REQ-0056, REQ-0059].
        
        Args:
            column_name: Name of column
            width: Width in pixels
        
        Raises:
            ValueError: If width is invalid (< 50)
        """
        if width < 50:
            raise ValueError(f"Column width must be at least 50px, got {width}")
        
        try:
            config_data = read_json(self.config_path) if self.config_path.exists() else {}
            
            # Ensure database_editor section exists
            if "database_editor" not in config_data:
                config_data["database_editor"] = {}
            if "column_widths" not in config_data["database_editor"]:
                config_data["database_editor"]["column_widths"] = {}
            
            config_data["database_editor"]["column_widths"][column_name] = width
            
            ensure_directory_exists(self.config_path.parent)
            write_json(self.config_path, config_data)
            logger.debug(f"Column width saved: {column_name} = {width}px")
        except Exception as e:
            logger.error(f"Failed to set column width for {column_name}: {e}")
    
    def get_all_column_widths(self) -> dict:
        """
        Get all saved column widths from config [REQ-0060].
        
        Returns:
            Dictionary of column_name -> width_px. Empty dict if section missing.
        """
        try:
            config_data = read_json(self.config_path) if self.config_path.exists() else {}
            widths = config_data.get("database_editor", {}).get("column_widths", {})
            
            # Validate all widths are positive
            valid_widths = {col: w for col, w in widths.items() if isinstance(w, int) and w > 0}
            
            if len(valid_widths) != len(widths):
                logger.warning(f"Some invalid column widths found in config, filtered to valid ones")
            
            return valid_widths
        except Exception as e:
            logger.warning(f"Failed to get all column widths: {e}")
            return {}
    
    def save_column_widths(self, widths_dict: dict) -> None:
        """
        Save all column widths to config.json [REQ-0059].
        
        Args:
            widths_dict: Dictionary of column_name -> width_px
        
        Raises:
            ConfigurationException: If save operation fails
        """
        try:
            config_data = read_json(self.config_path) if self.config_path.exists() else {}
            
            # Validate widths
            for col_name, width in widths_dict.items():
                if not isinstance(width, int) or width < 50:
                    logger.warning(f"Skipping invalid width for {col_name}: {width}")
                    continue
            
            # Ensure database_editor section exists
            if "database_editor" not in config_data:
                config_data["database_editor"] = {}
            
            config_data["database_editor"]["column_widths"] = widths_dict
            
            ensure_directory_exists(self.config_path.parent)
            write_json(self.config_path, config_data)
            logger.info(f"Saved {len(widths_dict)} column widths to config")
        except Exception as e:
            raise ConfigurationException(f"Failed to save column widths: {e}") from e

    # ===== Dialog Window Size Management Methods [REQ-0061] =====

    def get_dialog_window_size(self) -> Tuple[int, int]:
        """
        Get saved dialog window size from config [REQ-0061].
        
        Returns:
            Tuple of (width, height) in pixels. Defaults to (900, 600) if missing or invalid.
        """
        try:
            config_data = read_json(self.config_path) if self.config_path.exists() else {}
            window_config = config_data.get("database_editor", {}).get("window", {})
            
            width = window_config.get("width")
            height = window_config.get("height")
            
            # Validate: must be integers within reasonable bounds
            if (isinstance(width, int) and isinstance(height, int) and
                0 < width < 10000 and 0 < height < 10000):
                logger.debug(f"Loaded dialog window size from config: {width}x{height}")
                return (width, height)
            
            logger.warning(f"Invalid dialog window config: {window_config}, using defaults (900x600)")
            return (900, 600)
        except Exception as e:
            logger.error(f"Error reading dialog window config: {e}")
            return (900, 600)
    
    def save_dialog_window_size(self, width: int, height: int) -> None:
        """
        Save dialog window size to config [REQ-0061].
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
        
        Raises:
            ConfigurationException: If save operation fails
        """
        try:
            # Validate dimensions
            if not (isinstance(width, int) and isinstance(height, int) and
                    0 < width < 10000 and 0 < height < 10000):
                logger.warning(f"Skipping invalid window size: {width}x{height} (must be 0 < size < 10000)")
                return
            
            config_data = read_json(self.config_path) if self.config_path.exists() else {}
            
            # Ensure nested structure exists
            if "database_editor" not in config_data:
                config_data["database_editor"] = {}
            if "window" not in config_data["database_editor"]:
                config_data["database_editor"]["window"] = {}
            
            # Save dimensions
            config_data["database_editor"]["window"]["width"] = width
            config_data["database_editor"]["window"]["height"] = height
            
            ensure_directory_exists(self.config_path.parent)
            write_json(self.config_path, config_data)
            logger.info(f"Saved dialog window size to config: {width}x{height}")
        except Exception as e:
            raise ConfigurationException(f"Failed to save dialog window size: {e}") from e
