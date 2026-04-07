"""
Error handling utilities for the application [REQ-0027].

Provides centralized error handling, logging, and user-friendly error messages.
"""

import traceback
from typing import Tuple, Optional, Type

from app.exceptions import NameDaysAppException
from app.utils.logger import get_logger

logger = get_logger(__name__)


def handle_exception(
    exception: Exception,
    context: str = "",
    reraise: bool = False,
    user_friendly: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Handle an exception with logging and error reporting [REQ-0027].
    
    Args:
        exception: Exception to handle
        context: Context description for logging
        reraise: Whether to re-raise the exception after handling
        user_friendly: Whether to return user-friendly error message
    
    Returns:
        Tuple of (success, error_message)
        - success: False if exception occurred
        - error_message: User-friendly message if user_friendly=True, else None
    
    Raises:
        Exception: If reraise=True, the original exception is re-raised
    """
    # Log the error
    if context:
        logger.error(f"Error in {context}: {str(exception)}")
    else:
        logger.error(f"Exception occurred: {str(exception)}")
    
    # Log full traceback at debug level
    logger.debug(f"Traceback:\n{traceback.format_exc()}")
    
    # Get user-friendly message
    error_msg = None
    if user_friendly:
        error_msg = get_user_friendly_message(exception)
    
    # Re-raise if requested
    if reraise:
        raise exception
    
    return False, error_msg


def get_user_friendly_message(exception: Exception) -> str:
    """
    Convert exception to user-friendly error message.
    
    Args:
        exception: Exception to convert
    
    Returns:
        User-friendly error message
    """
    if isinstance(exception, NameDaysAppException):
        return exception.message
    
    exception_type = type(exception).__name__
    message = str(exception)
    
    # Map common exceptions to friendly messages
    friendly_messages = {
        "FileNotFoundError": "The requested file could not be found.",
        "PermissionError": "You don't have permission to perform this action.",
        "ValueError": "Invalid input value provided.",
        "KeyError": "Required data was not found.",
        "ConnectionError": "Failed to connect to the server.",
        "TimeoutError": "Operation timed out. Please try again.",
        "IOError": "An input/output error occurred. Please check your file system.",
        "OSError": "An operating system error occurred.",
    }
    
    if exception_type in friendly_messages:
        return friendly_messages[exception_type]
    
    # Try to extract useful info from message
    if message:
        return f"An error occurred: {message}"
    
    return f"An unexpected {exception_type} occurred."


def log_exception(
    exception: Exception,
    level: str = "ERROR",
    context: str = ""
) -> None:
    """
    Log exception at specified level.
    
    Args:
        exception: Exception to log
        level: Log level (ERROR, WARNING, DEBUG, INFO)
        context: Context description
    """
    log_func = getattr(logger, level.lower(), logger.error)
    
    if context:
        log_func(f"{context}: {str(exception)}")
    else:
        log_func(str(exception))
    
    logger.debug(f"Traceback:\n{traceback.format_exc()}")


def safe_execute(
    func,
    *args,
    default_return=None,
    log_errors: bool = True,
    **kwargs
):
    """
    Safely execute a function with exception handling.
    
    Args:
        func: Function to execute
        *args: Positional arguments
        default_return: Value to return if exception occurs
        log_errors: Whether to log errors
        **kwargs: Keyword arguments
    
    Returns:
        Function result or default_return if exception occurs
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            logger.error(f"Error executing {func.__name__}: {str(e)}")
        return default_return


def require_non_none(
    value,
    name: str,
    exception_class: Type[Exception] = ValueError
) -> None:
    """
    Require that a value is not None.
    
    Args:
        value: Value to check
        name: Name of parameter for error message
        exception_class: Exception class to raise
    
    Raises:
        Exception: If value is None
    """
    if value is None:
        raise exception_class(f"Required parameter '{name}' cannot be None")


def require_not_empty(
    value: str,
    name: str,
    exception_class: Type[Exception] = ValueError
) -> None:
    """
    Require that a string value is not empty.
    
    Args:
        value: String value to check
        name: Name of parameter for error message
        exception_class: Exception class to raise
    
    Raises:
        Exception: If value is empty
    """
    if not value or not str(value).strip():
        raise exception_class(f"Required parameter '{name}' cannot be empty")


def ensure_type(
    value,
    expected_type: Type,
    name: str,
    exception_class: Type[Exception] = TypeError
) -> None:
    """
    Ensure a value is of expected type.
    
    Args:
        value: Value to check
        expected_type: Expected type
        name: Name of parameter for error message
        exception_class: Exception class to raise
    
    Raises:
        Exception: If value is not expected type
    """
    if not isinstance(value, expected_type):
        raise exception_class(
            f"Parameter '{name}' must be {expected_type.__name__}, "
            f"got {type(value).__name__}"
        )
