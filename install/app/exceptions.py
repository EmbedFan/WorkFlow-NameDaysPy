"""
Custom exception classes for the application.

Used for error handling and exception-specific behaviors [REQ-0027].
"""


class NameDaysAppException(Exception):
    """Base exception for all application-specific exceptions."""
    
    def __init__(self, message: str, error_code: str = "GENERAL_ERROR"):
        """
        Initialize exception with message and error code.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code for logging
        """
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class DatabaseException(NameDaysAppException):
    """Raised when database operations fail [REQ-0017, REQ-0021, REQ-0037]."""
    
    def __init__(self, message: str, operation: str = ""):
        """
        Initialize database exception.
        
        Args:
            message: Error message
            operation: Type of operation that failed (e.g., 'read', 'write')
        """
        self.operation = operation
        super().__init__(message, f"DB_ERROR_{operation.upper()}")


class ValidationException(NameDaysAppException):
    """Raised when data validation fails [REQ-0040]."""
    
    def __init__(self, message: str, field: str = ""):
        """
        Initialize validation exception.
        
        Args:
            message: Error message
            field: Name of field that failed validation
        """
        self.field = field
        super().__init__(message, f"VALIDATION_ERROR_{field.upper()}")


class ConfigurationException(NameDaysAppException):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str):
        """Initialize configuration exception."""
        super().__init__(message, "CONFIG_ERROR")


class EmailException(NameDaysAppException):
    """Raised when email operations fail [REQ-0007, REQ-0016, REQ-0019, REQ-0052]."""
    
    def __init__(self, message: str, recipient: str = ""):
        """
        Initialize email exception.
        
        Args:
            message: Error message
            recipient: Email recipient that failed
        """
        self.recipient = recipient
        super().__init__(message, "EMAIL_ERROR")


class AuthenticationException(NameDaysAppException):
    """Raised when authentication fails [REQ-0016, REQ-0052]."""
    
    def __init__(self, message: str, service: str = ""):
        """
        Initialize authentication exception.
        
        Args:
            message: Error message
            service: Service that failed to authenticate
        """
        self.service = service
        super().__init__(message, f"AUTH_ERROR_{service.upper()}")


class WindowsIntegrationException(NameDaysAppException):
    """Raised when Windows integration operations fail [REQ-0002, REQ-0051]."""
    
    def __init__(self, message: str, operation: str = ""):
        """
        Initialize Windows integration exception.
        
        Args:
            message: Error message
            operation: Type of operation that failed
        """
        self.operation = operation
        super().__init__(message, f"WINDOWS_ERROR_{operation.upper()}")


class FileOperationException(NameDaysAppException):
    """Raised when file operations fail."""
    
    def __init__(self, message: str, file_path: str = ""):
        """
        Initialize file operation exception.
        
        Args:
            message: Error message
            file_path: Path to file that failed
        """
        self.file_path = file_path
        super().__init__(message, "FILE_ERROR")


class NotificationException(NameDaysAppException):
    """Raised when notification operations fail [REQ-0005, REQ-0009]."""
    
    def __init__(self, message: str):
        """Initialize notification exception."""
        super().__init__(message, "NOTIFICATION_ERROR")


class MonitoringException(NameDaysAppException):
    """Raised when background monitoring fails [REQ-0022]."""
    
    def __init__(self, message: str):
        """Initialize monitoring exception."""
        super().__init__(message, "MONITORING_ERROR")


class DateFormatException(ValidationException):
    """Raised when date format is invalid [REQ-0023, REQ-0040]."""
    
    def __init__(self, message: str, value: str = ""):
        """Initialize date format exception."""
        super().__init__(message, "date")
        self.value = value


class EmailFormatException(ValidationException):
    """Raised when email format is invalid [REQ-0034, REQ-0040]."""
    
    def __init__(self, message: str, value: str = ""):
        """Initialize email format exception."""
        super().__init__(message, "email")
        self.value = value
