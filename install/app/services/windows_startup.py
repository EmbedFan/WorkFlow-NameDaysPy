"""
Windows startup integration manager [REQ-0002, REQ-0051].

Manages Windows registry entries for application auto-launch at startup.
"""

import winreg
from pathlib import Path
from typing import Optional
import re

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
        
        Registers run_hidden.vbs to start at Windows system startup.
        The VBScript runs hidden and launches the application in the background.
        """
        startup_command = ""
        try:
            logger.debug(f"enable_auto_launch called with app_path: {app_path}")
            
            # Extract project root from main.py path in app_path or sys.argv
            # app_path format: "C:\...\python.exe "C:\...\main.py"" or similar
            # Try multiple patterns to handle different launch scenarios
            main_py_path = None
            
            # Pattern 1: Look for main.py in quotes (IDE/standard launch)
            match = re.search(r'"([^"]+main\.py)"', app_path)
            if match:
                main_py_path = Path(match.group(1))
                logger.debug(f"Found main.py from pattern 1: {main_py_path}")
            else:
                # Pattern 2: Look for any .py file in quotes (VBScript or alternative launch)
                match = re.search(r'"([^"]+\.py)"', app_path)
                if match:
                    main_py_path = Path(match.group(1))
                    logger.debug(f"Found Python file from pattern 2: {main_py_path}")
                else:
                    # Pattern 3: Last resort - try to use current working directory + main.py
                    logger.debug(f"Could not extract Python file path from app_path, trying fallback")
                    fallback_path = Path.cwd() / "main.py"
                    if fallback_path.exists():
                        main_py_path = fallback_path
                        logger.debug(f"Using fallback path: {main_py_path}")
            
            if not main_py_path:
                logger.error(f"Could not extract main.py path from: {app_path}")
                raise WindowsIntegrationException(
                    f"Invalid app_path format: {app_path}. Expected path to main.py.",
                    "invalid_path"
                )
            
            project_root = main_py_path.parent
            vbs_launcher = project_root / "run_hidden.vbs"
            
            if not vbs_launcher.exists():
                raise WindowsIntegrationException(
                    f"VBScript launcher not found at {vbs_launcher}. Create run_hidden.vbs in project root.",
                    "missing_wrapper"
                )
            
            # Register VBScript for startup using Windows Script Host
            # Format: cscript.exe "C:\full\path\to\run_hidden.vbs"
            # IMPORTANT: Must use absolute path so Windows can find it at startup
            startup_command = f'cscript.exe "{vbs_launcher.resolve()}"'
            logger.info(f"Prepared auto-launch command: '{startup_command}'")
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                STARTUP_REGISTRY_PATH,
                0,
                winreg.KEY_WRITE
            )
            
            winreg.SetValueEx(
                key,
                STARTUP_REGISTRY_KEY,
                0,
                winreg.REG_SZ,
                startup_command
            )
            
            winreg.CloseKey(key)
            logger.info(f"Auto-launch enabled for startup: {startup_command}")
            return True
        
        except WindowsIntegrationException:
            raise
        except Exception as e:
            logger.error(f"Failed to enable auto-launch: {e} | app_path: '{app_path}' | startup_command: '{startup_command}'")
            raise WindowsIntegrationException(f"Failed to enable auto-launch: {e}") from e
    
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
