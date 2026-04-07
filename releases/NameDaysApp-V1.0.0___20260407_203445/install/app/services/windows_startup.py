"""
Windows startup integration manager [REQ-0002, REQ-0051].

Manages Windows registry entries for application auto-launch at startup.
"""

import winreg
from typing import Optional

from app.utils import get_logger
from app.exceptions import WindowsIntegrationException
from app.constants import STARTUP_REGISTRY_PATH, STARTUP_REGISTRY_KEY

logger = get_logger(__name__)


class WindowsStartupManager:
    """
    Manage Windows startup integration [REQ-0002, REQ-0051].
    
    Handles Windows registry operations for auto-launch configuration.
    """
    
    def __init__(self, app_path: Optional[str] = None):
        """
        Initialize Windows startup manager [REQ-0051].
        
        Args:
            app_path: Path to application executable
        """
        self.app_path = app_path
    
    def enable_auto_launch(self, app_path: str) -> bool:
        """
        Register application for auto-launch at startup [REQ-0002, REQ-0051].
        
        Adds Windows registry entry under HKEY_CURRENT_USER.
        
        Args:
            app_path: Full path to application executable
        
        Returns:
            True if successful, False otherwise
        
        Raises:
            WindowsIntegrationException: If registry operation fails
        """
        try:
            self.app_path = app_path
            
            # Open registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                STARTUP_REGISTRY_PATH,
                0,
                winreg.KEY_WRITE
            )
            
            # Set registry value
            winreg.SetValueEx(
                key,
                STARTUP_REGISTRY_KEY,
                0,
                winreg.REG_SZ,
                app_path
            )
            
            winreg.CloseKey(key)
            logger.info(f"Auto-launch enabled for: {app_path}")
            return True
        
        except WindowsError as e:
            logger.error(f"Registry error enabling auto-launch: {e}")
            raise WindowsIntegrationException(
                f"Failed to enable auto-launch: {e}",
                "registry_write"
            ) from e
        except Exception as e:
            logger.error(f"Error enabling auto-launch: {e}")
            raise WindowsIntegrationException(
                f"Failed to enable auto-launch: {e}",
                "enable"
            ) from e
    
    def disable_auto_launch(self) -> bool:
        """
        Unregister application from auto-launch [REQ-0002, REQ-0051].
        
        Removes Windows registry entry.
        
        Returns:
            True if successful, False otherwise
        
        Raises:
            WindowsIntegrationException: If registry operation fails
        """
        try:
            # Open registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                STARTUP_REGISTRY_PATH,
                0,
                winreg.KEY_WRITE
            )
            
            # Delete registry value
            try:
                winreg.DeleteValue(key, STARTUP_REGISTRY_KEY)
            except WindowsError:
                # Value doesn't exist, that's ok
                pass
            
            winreg.CloseKey(key)
            logger.info("Auto-launch disabled")
            return True
        
        except WindowsError as e:
            logger.error(f"Registry error disabling auto-launch: {e}")
            raise WindowsIntegrationException(
                f"Failed to disable auto-launch: {e}",
                "registry_write"
            ) from e
        except Exception as e:
            logger.error(f"Error disabling auto-launch: {e}")
            raise WindowsIntegrationException(
                f"Failed to disable auto-launch: {e}",
                "disable"
            ) from e
    
    def is_auto_launch_enabled(self) -> bool:
        """
        Check if auto-launch is currently enabled [REQ-0002].
        
        Returns:
            True if auto-launch is enabled, False otherwise
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                STARTUP_REGISTRY_PATH,
                0,
                winreg.KEY_READ
            )
            
            try:
                value, _ = winreg.QueryValueEx(key, STARTUP_REGISTRY_KEY)
                winreg.CloseKey(key)
                return bool(value)
            except WindowsError:
                winreg.CloseKey(key)
                return False
        
        except Exception as e:
            logger.debug(f"Error checking auto-launch status: {e}")
            return False
    
    def is_running_at_startup(self) -> bool:
        """
        Detect if application started at system startup [REQ-0002].
        
        Note: This would require parent process inspection or environment variables.
        Not fully implementable without additional context.
        
        Returns:
            True if likely started at startup, False otherwise
        """
        # This would need to check parent process or passed startup argument
        # For now, return whether auto-launch is configured
        return self.is_auto_launch_enabled()
    
    def get_auto_launch_path(self) -> Optional[str]:
        """
        Get the currently configured auto-launch path.
        
        Returns:
            Application path if configured, None otherwise
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                STARTUP_REGISTRY_PATH,
                0,
                winreg.KEY_READ
            )
            
            try:
                value, _ = winreg.QueryValueEx(key, STARTUP_REGISTRY_KEY)
                winreg.CloseKey(key)
                return value if value else None
            except WindowsError:
                winreg.CloseKey(key)
                return None
        
        except Exception as e:
            logger.debug(f"Error getting auto-launch path: {e}")
            return None
    
    def _get_registry_path(self) -> str:
        """
        Get registry key path for app startup.
        
        Returns:
            Registry path string
        """
        return STARTUP_REGISTRY_PATH
    
    def _write_registry(self, value: str) -> bool:
        """
        Write to Windows registry.
        
        Args:
            value: Value to write
        
        Returns:
            True if successful
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                STARTUP_REGISTRY_PATH,
                0,
                winreg.KEY_WRITE
            )
            winreg.SetValueEx(key, STARTUP_REGISTRY_KEY, 0, winreg.REG_SZ, value)
            winreg.CloseKey(key)
            return True
        except Exception:
            return False
    
    def _read_registry(self) -> Optional[str]:
        """
        Read from Windows registry.
        
        Returns:
            Registry value or None if not found
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                STARTUP_REGISTRY_PATH,
                0,
                winreg.KEY_READ
            )
            value, _ = winreg.QueryValueEx(key, STARTUP_REGISTRY_KEY)
            winreg.CloseKey(key)
            return value
        except Exception:
            return None
    
    def _delete_registry(self) -> bool:
        """
        Delete registry key.
        
        Returns:
            True if successful
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                STARTUP_REGISTRY_PATH,
                0,
                winreg.KEY_WRITE
            )
            winreg.DeleteValue(key, STARTUP_REGISTRY_KEY)
            winreg.CloseKey(key)
            return True
        except Exception:
            return False
