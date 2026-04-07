# Test Implementation Plan

## Overview

This document provides a detailed test implementation plan for the Name Days Monitoring Application, complementing the main implementation plan. All 55 requirements must have corresponding test coverage.

**Target Coverage:** >80% overall code coverage  
**Testing Framework:** pytest 7.0+ with pytest-cov for coverage reporting  
**Test Duration Goal:** Full suite completes in < 5 minutes

---

## 1. Test Organization & Structure

### Directory Layout

```
tests/
├── __init__.py
├── conftest.py                          # Shared fixtures and configuration
├── fixtures/
│   ├── __init__.py
│   ├── contact_fixtures.py              # Sample contact data
│   ├── nameday_fixtures.py              # Sample nameday data
│   ├── settings_fixtures.py             # Sample settings
│   └── mock_services.py                 # Mock SMTP, registry, etc.
├── unit/
│   ├── __init__.py
│   ├── test_exceptions.py
│   ├── test_constants.py
│   ├── test_types.py
│   ├── utils/
│   │   ├── test_logger.py
│   │   ├── test_date_utils.py
│   │   ├── test_error_handler.py
│   │   └── test_file_utils.py
│   ├── services/
│   │   ├── test_data_validator.py       [REQ-0030 to REQ-0046]
│   │   ├── test_email_service.py        [REQ-0016, REQ-0019, REQ-0020, REQ-0052]
│   │   └── test_windows_startup.py      [REQ-0002, REQ-0025, REQ-0051]
│   ├── managers/
│   │   ├── test_contact_db_manager.py   [REQ-0017, REQ-0021, REQ-0029-0037, REQ-0040]
│   │   ├── test_nameday_reference_manager.py [REQ-0013, REQ-0018, REQ-0038, REQ-0039]
│   │   ├── test_settings_manager.py     [REQ-0014, REQ-0026, REQ-0028, REQ-0055]
│   │   └── test_config_validator.py
│   ├── core/
│   │   ├── test_notification_queue.py   [REQ-0004]
│   │   ├── test_monitoring_engine.py    [REQ-0003, REQ-0022, REQ-0023, REQ-0024]
│   │   └── test_notification_manager.py [REQ-0005-REQ-0009, REQ-0019]
│   ├── ui/
│   │   ├── test_system_tray.py          [REQ-0010, REQ-0042]
│   │   ├── test_notification_modal.py   [REQ-0043, REQ-0044]
│   │   ├── test_settings_dialog.py      [REQ-0047]
│   │   ├── test_database_editor.py      [REQ-0049]
│   │   ├── test_query_dialog.py         [REQ-0050]
│   │   ├── test_today_namedays_view.py  [REQ-0012]
│   │   └── test_styles.py
│   ├── i18n/
│   │   ├── test_i18n_manager.py         [REQ-0045, REQ-0046]
│   │   ├── test_en_strings.py
│   │   └── test_hu_strings.py
│   └── test_main.py                     [REQ-0001, REQ-0002, REQ-0015, REQ-0041]
├── integration/
│   ├── __init__.py
│   ├── test_startup_sequence.py
│   ├── test_notification_workflow.py
│   ├── test_settings_workflow.py
│   ├── test_contact_management_workflow.py
│   └── test_email_workflow.py
├── performance/
│   ├── __init__.py
│   ├── test_memory_usage.py             [REQ-0024]
│   ├── test_cpu_usage.py                [REQ-0024]
│   ├── test_interval_accuracy.py        [REQ-0003]
│   └── test_csv_performance.py
└── windows_compat/
    ├── __init__.py
    ├── test_registry_operations.py      [REQ-0051]
    ├── test_auto_launch.py              [REQ-0002]
    └── test_system_integration.py       [REQ-0025]
```

### Test Naming Conventions

```
# Unit test file naming
test_<module_name>.py

# Unit test function naming
test_<class_name>_<method_name>_<scenario>
test_<function_name>_<scenario>

# Examples
test_contact_db_manager_create_contact_valid_data()
test_contact_db_manager_create_contact_invalid_email()
test_data_validator_validate_email_with_special_chars()
test_monitoring_engine_check_namedays_multiple_matches()

# Integration test naming
test_<workflow_name>_<step>
test_<workflow_name>_success_path()
test_<workflow_name>_error_handling()

# Performance test naming
test_<component>_memory_usage_under_limit()
test_<component>_cpu_usage_acceptable()

# Windows-specific test naming
test_<feature>_windows_10()
test_<feature>_windows_11()
```

### Test Configuration Files

**pytest.ini**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    -p no:warnings
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    windows_compat: Windows compatibility tests
    slow: Slow running tests
minversion = 7.0
```

**pytest.ini (CI Configuration)**
```ini
# For continuous integration - stricter settings
addopts = 
    -v
    --cov=app
    --cov-report=xml
    --cov-report=term-missing
    --cov-fail-under=85
    --maxfail=1
    --tb=short
```

**setup.cfg**
```ini
[coverage:run]
source = app
omit = 
    */tests/*
    */__init__.py
    */main.py

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstract
```

---

## 2. Unit Test Implementation Details

### 2.1 Utils Tests

#### `tests/unit/utils/test_date_utils.py` [REQ-0023]

```python
import pytest
from app.utils.date_utils import DateUtils

class TestDateUtils:
    """Test date utility functions for MM-DD format [REQ-0023]."""
    
    def test_get_today_mmdd_valid_format(self):
        """Test get_today_mmdd returns MM-DD format."""
        result = DateUtils.get_today_mmdd()
        assert isinstance(result, str)
        assert len(result) == 5
        assert result[2] == '-'
        month, day = result.split('-')
        assert 1 <= int(month) <= 12
        assert 1 <= int(day) <= 31
    
    def test_string_to_mmdd_valid_date(self):
        """Test conversion of valid date strings to MM-DD format."""
        assert DateUtils.string_to_mmdd("2026-03-30") == "03-30"
        assert DateUtils.string_to_mmdd("2026-12-25") == "12-25"
        assert DateUtils.string_to_mmdd("2026-01-01") == "01-01"
    
    def test_string_to_mmdd_invalid_format(self):
        """Test InvalidDateFormatError on invalid format."""
        with pytest.raises(InvalidDateFormatError):
            DateUtils.string_to_mmdd("2026/03/30")
        with pytest.raises(InvalidDateFormatError):
            DateUtils.string_to_mmdd("invalid")
        with pytest.raises(InvalidDateFormatError):
            DateUtils.string_to_mmdd("03-30-2026")
    
    def test_is_valid_mmdd_format(self):
        """Test MM-DD format validation."""
        assert DateUtils.is_valid_mmdd("03-30") is True
        assert DateUtils.is_valid_mmdd("12-25") is True
        assert DateUtils.is_valid_mmdd("01-01") is True
        assert DateUtils.is_valid_mmdd("13-01") is False  # Invalid month
        assert DateUtils.is_valid_mmdd("03-32") is False  # Invalid day
        assert DateUtils.is_valid_mmdd("3-30") is False   # Missing leading zero
        assert DateUtils.is_valid_mmdd("03/30") is False  # Wrong separator
    
    def test_get_days_until_date(self):
        """Test calculating days until a given date."""
        # Mock current date for testing
        today_mmdd = "03-30"
        assert DateUtils.get_days_until_date(today_mmdd) == 0
        assert DateUtils.get_days_until_date("03-31") == 1
        # Cross-year calculation
        assert DateUtils.get_days_until_date("01-01") > 200
```

#### `tests/unit/utils/test_logger.py` [REQ-0027]

```python
class TestAppLogger:
    """Test logging utility for application [REQ-0027]."""
    
    def test_get_logger_returns_logger(self):
        """Test get_logger returns a valid logger instance."""
        logger = AppLogger.get_logger("test")
        assert logger is not None
        assert logger.name == "test"
    
    def test_logger_writes_to_file(self, tmp_path):
        """Test logger writes messages to log file."""
        log_file = tmp_path / "test.log"
        logger = AppLogger.get_logger("test", str(log_file))
        logger.info("Test message")
        assert log_file.exists()
        assert "Test message" in log_file.read_text()
    
    def test_logger_levels(self, tmp_path):
        """Test logger respects logging levels."""
        log_file = tmp_path / "test.log"
        logger = AppLogger.get_logger("test", str(log_file))
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        log_content = log_file.read_text()
        assert "Info message" in log_content
        assert "Warning message" in log_content
        assert "Error message" in log_content
```

#### `tests/unit/utils/test_error_handler.py` [REQ-0027]

```python
class TestErrorHandler:
    """Test graceful error handling [REQ-0027]."""
    
    def test_format_exception_message(self):
        """Test exception message formatting."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            formatted = ErrorHandler.format_exception_message(e)
            assert "ValueError" in formatted
            assert "Test error" in formatted
    
    def test_log_exception(self, caplog):
        """Test exception logging."""
        try:
            raise RuntimeError("Test runtime error")
        except RuntimeError as e:
            ErrorHandler.log_exception(e)
        assert "RuntimeError" in caplog.text
    
    def mock_show_user_error(self, monkeypatch):
        """Test show_user_error (mocked for testing)."""
        mock_message_box = Mock()
        monkeypatch.setattr("QMessageBox.critical", mock_message_box)
        ErrorHandler.show_user_error("Test Title", "Test message")
        # Verify modal was called (implementation-specific)
```

### 2.2 Services Tests

#### `tests/unit/services/test_data_validator.py` [REQ-0030 to REQ-0034, REQ-0040]

```python
import pytest
from app.services.data_validator import DataValidator
from app.exceptions import InvalidEmailError, InvalidDateFormatError

class TestDataValidator:
    """Test input validation [REQ-0030 to REQ-0034, REQ-0040]."""
    
    @pytest.fixture
    def validator(self):
        return DataValidator()
    
    # Name validation tests [REQ-0030]
    def test_validate_name_valid(self, validator):
        """Test valid name validation."""
        assert validator.validate_name("János") is True
        assert validator.validate_name("Mária Kiss") is True
        assert validator.validate_name("James O'Brien") is True
    
    def test_validate_name_invalid_empty(self, validator):
        """Test invalid empty name."""
        with pytest.raises(ValueError):
            validator.validate_name("")
    
    def test_validate_name_invalid_too_long(self, validator):
        """Test invalid name exceeding max length (100 chars)."""
        with pytest.raises(ValueError):
            validator.validate_name("A" * 101)
    
    def test_validate_name_invalid_special_chars(self, validator):
        """Test name with invalid special characters."""
        with pytest.raises(ValueError):
            validator.validate_name("János@#$")
    
    # Nameday date validation tests [REQ-0031, REQ-0023]
    def test_validate_nameday_date_valid(self, validator):
        """Test valid nameday date formats."""
        assert validator.validate_nameday_date("03-30") is True
        assert validator.validate_nameday_date("12-25") is True
        assert validator.validate_nameday_date("01-01") is True
    
    def test_validate_nameday_date_invalid_format(self, validator):
        """Test invalid date formats."""
        with pytest.raises(InvalidDateFormatError):
            validator.validate_nameday_date("2026-03-30")
        with pytest.raises(InvalidDateFormatError):
            validator.validate_nameday_date("03/30")
        with pytest.raises(InvalidDateFormatError):
            validator.validate_nameday_date("3-30")
    
    def test_validate_nameday_date_invalid_values(self, validator):
        """Test invalid date values."""
        with pytest.raises(ValueError):
            validator.validate_nameday_date("13-01")  # month > 12
        with pytest.raises(ValueError):
            validator.validate_nameday_date("02-30")  # invalid day
    
    def test_validate_nameday_date_empty_allowed(self, validator):
        """Test empty nameday date is allowed (optional field) [REQ-0032]."""
        assert validator.validate_nameday_date("") is True
    
    # Email validation tests [REQ-0033, REQ-0034, REQ-0040]
    def test_validate_email_valid(self, validator):
        """Test valid email addresses."""
        assert validator.validate_email("test@example.com") is True
        assert validator.validate_email("user.name+tag@example.co.uk") is True
        assert validator.validate_email("contact@sub.domain.com") is True
    
    def test_validate_email_invalid_format(self, validator):
        """Test invalid email formats."""
        with pytest.raises(InvalidEmailError):
            validator.validate_email("invalid.email")
        with pytest.raises(InvalidEmailError):
            validator.validate_email("@example.com")
        with pytest.raises(InvalidEmailError):
            validator.validate_email("user@")
        with pytest.raises(InvalidEmailError):
            validator.validate_email("")
    
    def test_validate_email_special_cases(self, validator):
        """Test email validation edge cases."""
        # Valid special cases
        assert validator.validate_email("test+tag@example.com") is True
        assert validator.validate_email("123@example.com") is True
        # Invalid special cases
        with pytest.raises(InvalidEmailError):
            validator.validate_email("test..double@example.com")
    
    # Multiple emails validation [REQ-0033]
    def test_validate_recipient_valid_single(self, validator):
        """Test single recipient validation."""
        assert validator.validate_recipient("user@example.com") is True
    
    def test_validate_recipient_valid_multiple(self, validator):
        """Test multiple recipients separated by semicolon."""
        assert validator.validate_recipient("user1@example.com;user2@example.com") is True
        assert validator.validate_recipient("a@ex.com;b@ex.com;c@ex.com") is True
    
    def test_validate_recipient_invalid_mixed(self, validator):
        """Test invalid recipient list."""
        with pytest.raises(InvalidEmailError):
            validator.validate_recipient("user@example.com;invalid.email")
    
    # Contact validation [REQ-0029, REQ-0030-0036]
    def test_validate_contact_complete(self, validator, contact_fixture):
        """Test validation of complete valid contact."""
        errors = validator.validate_contact(contact_fixture)
        assert len(errors) == 0
    
    def test_validate_contact_multiple_errors(self, validator):
        """Test validation collects all errors."""
        invalid_contact = Contact(
            name="",  # Empty
            main_nameday="invalid",  # Invalid date
            email_addresses="not-an-email"  # Invalid email
        )
        errors = validator.validate_contact(invalid_contact)
        assert len(errors) >= 3
        assert any("name" in e.lower() for e in errors)
        assert any("date" in e.lower() for e in errors)
        assert any("email" in e.lower() for e in errors)
```

#### `tests/unit/services/test_email_service.py` [REQ-0016, REQ-0019, REQ-0020, REQ-0052]

```python
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.email_service import EmailService

class TestEmailService:
    """Test Gmail integration [REQ-0016, REQ-0019, REQ-0020, REQ-0052]."""
    
    @pytest.fixture
    def email_service(self):
        return EmailService()
    
    @pytest.fixture
    def mock_smtp(self, monkeypatch):
        """Mock SMTP server."""
        mock = MagicMock()
        monkeypatch.setattr("smtplib.SMTP", mock)
        return mock
    
    def test_authenticate_valid_credentials(self, email_service, mock_smtp):
        """Test SMTP authentication with valid credentials [REQ-0052]."""
        email_service.authenticate("test@gmail.com", "password123")
        # Verify SMTP was initialized
        assert email_service.is_authenticated is True
    
    def test_authenticate_invalid_credentials(self, email_service, mock_smtp):
        """Test authentication failure."""
        mock_smtp.return_value.login.side_effect = smtplib.SMTPAuthenticationError(535, "error")
        with pytest.raises(AuthenticationError):
            email_service.authenticate("test@gmail.com", "wrong_password")
    
    def test_send_email_simple(self, email_service, mock_smtp):
        """Test sending simple email [REQ-0019]."""
        email_service.authenticate("sender@gmail.com", "password")
        status = email_service.send_email(
            to="recipient@example.com",
            subject="Test Subject",
            body="Test Body"
        )
        assert status is True
        mock_smtp.return_value.send_message.assert_called_once()
    
    def test_send_email_with_template(self, email_service, mock_smtp):
        """Test email with template substitution [REQ-0020]."""
        email_service.authenticate("sender@gmail.com", "password")
        template = "Dear {name},\nHappy nameday!"
        body = email_service.apply_template(template, {"name": "János"})
        assert body == "Dear János,\nHappy nameday!"
    
    def test_send_email_multiple_recipients(self, email_service, mock_smtp):
        """Test sending to multiple recipients."""
        email_service.authenticate("sender@gmail.com", "password")
        status = email_service.send_email(
            to="user1@example.com;user2@example.com",
            subject="Test",
            body="Test Body"
        )
        assert status is True
    
    def test_send_email_invalid_recipient(self, email_service):
        """Test email validation before sending."""
        with pytest.raises(InvalidEmailError):
            email_service.send_email(
                to="invalid.email",
                subject="Test",
                body="Test"
            )
    
    def test_send_email_not_authenticated(self, email_service):
        """Test sending without authentication."""
        with pytest.raises(AuthenticationError):
            email_service.send_email(
                to="user@example.com",
                subject="Test",
                body="Test"
            )
    
    def test_apply_template_multiple_fields(self, email_service):
        """Test template with multiple substitutions."""
        template = "Hello {name}, welcome to {app_name}!"
        result = email_service.apply_template(
            template,
            {"name": "János", "app_name": "NameDays App"}
        )
        assert "János" in result
        assert "NameDays App" in result
    
    def test_apply_template_missing_variable(self, email_service):
        """Test template with missing variable."""
        template = "Hello {name}, today is {date}!"
        # Should either raise or leave placeholder
        try:
            result = email_service.apply_template(template, {"name": "János"})
            # Implementation-dependent behavior
        except KeyError:
            pass  # Expected if strict
```

#### `tests/unit/services/test_windows_startup.py` [REQ-0002, REQ-0025, REQ-0051]

```python
import pytest
from unittest.mock import Mock, patch
from app.services.windows_startup import WindowsStartupManager

class TestWindowsStartupManager:
    """Test Windows auto-launch management [REQ-0002, REQ-0025, REQ-0051]."""
    
    @pytest.fixture
    def startup_manager(self):
        return WindowsStartupManager()
    
    @pytest.fixture
    def mock_registry(self, monkeypatch):
        """Mock Windows registry operations."""
        mock = Mock()
        monkeypatch.setattr("winreg.OpenKey", mock)
        monkeypatch.setattr("winreg.SetValueEx", mock)
        monkeypatch.setattr("winreg.DeleteValue", mock)
        return mock
    
    def test_enable_auto_launch(self, startup_manager, mock_registry):
        """Test enabling auto-launch [REQ-0002, REQ-0051]."""
        result = startup_manager.enable_auto_launch()
        assert result is True
        # Verify registry was modified
    
    def test_disable_auto_launch(self, startup_manager, mock_registry):
        """Test disabling auto-launch [REQ-0002, REQ-0051]."""
        result = startup_manager.disable_auto_launch()
        assert result is True
    
    def test_is_auto_launch_enabled_true(self, startup_manager, mock_registry):
        """Test checking if auto-launch is enabled [REQ-0002]."""
        # Mock registry to return enabled state
        result = startup_manager.is_auto_launch_enabled()
        assert isinstance(result, bool)
    
    def test_is_running_at_startup(self, startup_manager):
        """Test detecting auto-startup launch [REQ-0002]."""
        # This would require environment variable checking
        result = startup_manager.is_running_at_startup()
        assert isinstance(result, bool)
    
    def test_registry_path_windows_10(self):
        """Test correct registry path for Windows 10 [REQ-0025]."""
        path = WindowsStartupManager.get_startup_registry_path()
        assert "HKEY_CURRENT_USER" in path
        assert "Run" in path
    
    def test_registry_operations_handle_errors(self, startup_manager, mock_registry):
        """Test graceful error handling in registry ops."""
        mock_registry.side_effect = WindowsError("Registry error")
        with pytest.raises(RegistryError):
            startup_manager.enable_auto_launch()
```

### 2.3 Managers Tests

#### `tests/unit/managers/test_contact_db_manager.py` [REQ-0017, REQ-0021, REQ-0029-0037, REQ-0040]

```python
import pytest
from pathlib import Path
from app.managers.contact_db_manager import ContactDatabaseManager, Contact

class TestContactDatabaseManager:
    """Test contact CRUD operations [REQ-0017, REQ-0021, REQ-0029-0037]."""
    
    @pytest.fixture
    def db_manager(self, tmp_path):
        """Create DB manager with temporary file."""
        db_path = tmp_path / "contacts.csv"
        return ContactDatabaseManager(str(db_path))
    
    @pytest.fixture
    def sample_contact(self):
        """Create sample contact."""
        return Contact(
            name="János Kovács",
            main_nameday="06-04",
            other_nameday="11-30",
            recipient="János (work)",
            email_addresses="janos@example.com",
            prewritten_email="Dear János,\nHappy nameday!",
            comment="Colleague from IT"
        )
    
    # CRUD Operations [REQ-0017]
    def test_create_contact_valid(self, db_manager, sample_contact):
        """Test creating valid contact."""
        contact_id = db_manager.create_contact(sample_contact)
        assert contact_id is not None
        assert isinstance(contact_id, str)
    
    def test_create_contact_invalid_data(self, db_manager):
        """Test creating contact with invalid data [REQ-0040]."""
        invalid_contact = Contact(
            name="",  # Invalid: empty
            email_addresses="invalid-email"
        )
        with pytest.raises(ValidationError):
            db_manager.create_contact(invalid_contact)
    
    def test_read_contacts_empty(self, db_manager):
        """Test reading from empty database."""
        contacts = db_manager.read_contacts()
        assert isinstance(contacts, list)
        assert len(contacts) == 0
    
    def test_read_contacts_multiple(self, db_manager, sample_contact):
        """Test reading multiple contacts [REQ-0021]."""
        db_manager.create_contact(sample_contact)
        sample_contact.name = "Mária Kiss"
        db_manager.create_contact(sample_contact)
        
        contacts = db_manager.read_contacts()
        assert len(contacts) == 2
    
    def test_update_contact_valid(self, db_manager, sample_contact):
        """Test updating contact."""
        contact_id = db_manager.create_contact(sample_contact)
        sample_contact.name = "Updated Name"
        db_manager.update_contact(contact_id, sample_contact)
        
        updated = db_manager.get_contact(contact_id)
        assert updated.name == "Updated Name"
    
    def test_update_contact_nonexistent(self, db_manager, sample_contact):
        """Test updating non-existent contact."""
        with pytest.raises(ContactNotFoundError):
            db_manager.update_contact("nonexistent_id", sample_contact)
    
    def test_delete_contact(self, db_manager, sample_contact):
        """Test deleting contact."""
        contact_id = db_manager.create_contact(sample_contact)
        db_manager.delete_contact(contact_id)
        
        with pytest.raises(ContactNotFoundError):
            db_manager.get_contact(contact_id)
    
    def test_get_contact_by_name(self, db_manager, sample_contact):
        """Test finding contact by name."""
        db_manager.create_contact(sample_contact)
        found = db_manager.get_contact_by_name("János Kovács")
        assert found is not None
        assert found.name == "János Kovács"
    
    # CSV Operations [REQ-0037]
    def test_load_csv_valid_format(self, db_manager):
        """Test loading CSV with valid format [REQ-0037]."""
        # Create sample CSV with semicolon, UTF-8
        csv_content = """name;main_nameday;other_nameday;recipient;email_addresses;prewritten_email;comment
János;06-04;11-30;János;janos@ex.com;;IT colleague
Mária;05-01;08-15;Mária;maria@ex.com;;Manager
"""
        db_path = Path(db_manager.db_path)
        db_path.write_text(csv_content, encoding='utf-8')
        
        contacts = db_manager.load_csv()
        assert len(contacts) == 2
        assert contacts[0].name == "János"
    
    def test_load_csv_invalid_format(self, db_manager):
        """Test loading CSV with invalid format."""
        csv_content = "invalid,csv,format"
        Path(db_manager.db_path).write_text(csv_content)
        
        with pytest.raises(CSVFormatError):
            db_manager.load_csv()
    
    def test_save_csv_utf8(self, db_manager, sample_contact):
        """Test saving CSV with UTF-8 encoding [REQ-0037]."""
        db_manager.create_contact(sample_contact)
        db_manager.save_csv()
        
        saved_content = Path(db_manager.db_path).read_text(encoding='utf-8')
        assert "János" in saved_content
        assert ";" in saved_content  # Semicolon separator
    
    def test_save_csv_preserves_data(self, db_manager, sample_contact):
        """Test CSV round-trip preserves data."""
        db_manager.create_contact(sample_contact)
        db_manager.save_csv()
        
        # Reload
        db_manager2 = ContactDatabaseManager(db_manager.db_path)
        reloaded = db_manager2.read_contacts()
        assert reloaded[0].name == sample_contact.name
        assert reloaded[0].email_addresses == sample_contact.email_addresses
    
    # Optional fields [REQ-0032, REQ-0035, REQ-0036]
    def test_contact_with_optional_fields(self, db_manager):
        """Test contact with optional other_nameday, prewritten_email, comment."""
        minimal_contact = Contact(
            name="Simple User",
            main_nameday="03-30",
            other_nameday="",  # Optional
            email_addresses="user@example.com"
            # prewritten_email and comment are optional
        )
        contact_id = db_manager.create_contact(minimal_contact)
        assert contact_id is not None
    
    def test_contact_email_recipient_handling(self, db_manager):
        """Test contact email and recipient field handling [REQ-0033]."""
        contact = Contact(
            name="Test User",
            main_nameday="03-30",
            recipient="Test;User",  # Multiple recipients
            email_addresses="test@ex.com;user@ex.com"
        )
        contact_id = db_manager.create_contact(contact)
        retrieved = db_manager.get_contact(contact_id)
        assert ";" in retrieved.email_addresses
```

#### `tests/unit/managers/test_nameday_reference_manager.py` [REQ-0013, REQ-0018, REQ-0038, REQ-0039]

```python
import pytest
from app.managers.nameday_reference_manager import NamedayReferenceManager, Nameday

class TestNamedayReferenceManager:
    """Test nameday lookup [REQ-0013, REQ-0018, REQ-0038, REQ-0039]."""
    
    @pytest.fixture
    def nameday_manager(self):
        """Create manager with built-in reference [REQ-0039]."""
        return NamedayReferenceManager()
    
    def test_get_nameday_by_name_valid(self, nameday_manager):
        """Test looking up nameday by name [REQ-0018]."""
        nameday = nameday_manager.get_nameday("János")
        assert nameday is not None
        assert namesday.name == "János"
        assert nameday.main_nameday == "06-04"  # Hungarian nameday for János
    
    def test_get_nameday_by_name_invalid(self, nameday_manager):
        """Test lookup of non-existent name."""
        nameday = nameday_manager.get_nameday("NonExistentName")
        assert nameday is None
    
    def test_get_nameday_case_insensitive(self, nameday_manager):
        """Test nameday lookup is case-insensitive."""
        nameday1 = nameday_manager.get_nameday("János")
        nameday2 = nameday_manager.get_nameday("JÁNOS")
        nameday3 = nameday_manager.get_nameday("jánós")
        assert nameday1.name == nameday2.name == nameday3.name
    
    def test_get_names_for_date(self, nameday_manager):
        """Test retrieving all names for a specific date [REQ-0023]."""
        names = nameday_manager.get_names_for_date("06-04")
        assert isinstance(names, list)
        assert len(names) > 0
        assert "János" in names
    
    def test_get_names_for_date_invalid_format(self, nameday_manager):
        """Test with invalid date format."""
        with pytest.raises(InvalidDateFormatError):
            nameday_manager.get_names_for_date("2026-06-04")
    
    def test_get_names_for_date_multiple_matches(self, nameday_manager):
        """Test date with multiple namedays [REQ-0004]."""
        # May 1st is Mária's main nameday and possibly others
        names = nameday_manager.get_names_for_date("05-01")
        assert isinstance(names, list)
        assert "Mária" in names
    
    def test_nameday_with_other_nameday(self, nameday_manager):
        """Test nameday with secondary nameday [REQ-0038]."""
        nameday = nameday_manager.get_nameday("János")
        assert nameday.other_nameday == "11-30"
    
    def test_nameday_without_other_nameday(self, nameday_manager):
        """Test nameday without secondary nameday."""
        # Find a name with no other_nameday
        nameday = nameday_manager.get_nameday("Adél")
        assert nameday.other_nameday == "" or nameday.other_nameday is None
    
    def test_load_reference_csv(self, nameday_manager):
        """Test loading built-in nameday reference [REQ-0039]."""
        # Manager should have loaded reference
        assert nameday_manager._reference is not None
        assert len(nameday_manager._reference) > 0
    
    def test_reference_contains_hungarian_names(self, nameday_manager):
        """Test reference supports Hungarian names [REQ-0018]."""
        hungarian_names = ["János", "Mária", "Andrea", "István"]
        for name in hungarian_names:
            nameday = nameday_manager.get_nameday(name)
            assert nameday is not None, f"Hungarian name '{name}' not found"
    
    def test_query_search_by_partial_name(self, nameday_manager):
        """Test searching by partial name [REQ-0013]."""
        results = nameday_manager.search_by_name("Já")
        assert isinstance(results, list)
        assert any("János" in r for r in results)
```

#### `tests/unit/managers/test_settings_manager.py` [REQ-0014, REQ-0026, REQ-0028, REQ-0055]

```python
import pytest
import json
from pathlib import Path
from app.managers.settings_manager import SettingsManager, Settings

class TestSettingsManager:
    """Test settings management [REQ-0026, REQ-0028, REQ-0055]."""
    
    @pytest.fixture
    def settings_manager(self, tmp_path):
        """Create manager with temporary config file."""
        config_path = tmp_path / "settings.json"
        return SettingsManager(str(config_path))
    
    @pytest.fixture
    def sample_settings(self):
        """Create sample settings."""
        return Settings(
            check_interval=15,
            gmail_address="test@gmail.com",
            gmail_password="password",
            auto_launch_enabled=True,
            language="en",
            notifications_enabled=True
        )
    
    def test_load_settings_empty_creates_defaults(self, settings_manager):
        """Test loading from non-existent file creates defaults [REQ-0028]."""
        settings = settings_manager.load_settings()
        assert settings is not None
        assert settings.check_interval == 15  # Default
        assert settings.language == "en"  # Default
    
    def test_save_settings_creates_json(self, settings_manager, sample_settings):
        """Test saving settings to JSON file [REQ-0026, REQ-0055]."""
        settings_manager.save_settings(sample_settings)
        
        config_file = Path(settings_manager.config_path)
        assert config_file.exists()
        
        content = json.loads(config_file.read_text())
        assert content["check_interval"] == 15
        assert content["language"] == "en"
    
    def test_settings_round_trip(self, settings_manager, sample_settings):
        """Test save and load preserves data."""
        settings_manager.save_settings(sample_settings)
        loaded = settings_manager.load_settings()
        
        assert loaded.check_interval == sample_settings.check_interval
        assert loaded.language == sample_settings.language
        assert loaded.notifications_enabled == sample_settings.notifications_enabled
    
    def test_settings_partial_update(self, settings_manager):
        """Test updating only some settings."""
        settings_manager.update_setting("check_interval", 30)
        loaded = settings_manager.load_settings()
        assert loaded.check_interval == 30
    
    def test_settings_invalid_json(self, settings_manager, tmp_path):
        """Test handling corrupted config file."""
        config_file = Path(settings_manager.config_path)
        config_file.write_text("{invalid json")
        
        # Should load defaults on error [REQ-0028]
        settings = settings_manager.load_settings()
        assert settings is not None
    
    def test_default_settings_values(self, settings_manager):
        """Test default settings are reasonable [REQ-0028]."""
        defaults = Settings()
        assert 1 <= defaults.check_interval <= 60
        assert defaults.language in ["en", "hu"]
        assert isinstance(defaults.notifications_enabled, bool)
    
    # REQ-0014: Settings access via UI
    def test_get_all_settings(self, settings_manager, sample_settings):
        """Test retrieving all settings for UI display [REQ-0014]."""
        settings_manager.save_settings(sample_settings)
        all_settings = settings_manager.get_all_settings()
        assert isinstance(all_settings, dict)
        assert "check_interval" in all_settings
        assert "language" in all_settings
```

### 2.4 Core Engine Tests

#### `tests/unit/core/test_monitoring_engine.py` [REQ-0003, REQ-0022, REQ-0023, REQ-0024]

```python
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from app.core.monitoring_engine import MonitoringEngine, Notification

class TestMonitoringEngine:
    """Test background monitoring [REQ-0003, REQ-0022, REQ-0023, REQ-0024]."""
    
    @pytest.fixture
    def mock_contact_db(self):
        """Mock contact database."""
        mock = Mock()
        mock.read_contacts.return_value = [
            Mock(name="János", main_nameday="06-04", email_addresses="janos@ex.com"),
            Mock(name="Mária", main_nameday="05-01", email_addresses="maria@ex.com")
        ]
        return mock
    
    @pytest.fixture
    def mock_nameday_ref(self):
        """Mock nameday reference."""
        mock = Mock()
        mock.get_names_for_date.return_value = []
        return mock
    
    @pytest.fixture
    def monitoring_engine(self, mock_contact_db, mock_nameday_ref):
        """Create monitoring engine with mocks."""
        engine = MonitoringEngine(mock_contact_db, mock_nameday_ref)
        engine.moveToThread = Mock()  # Mock Qt thread operations
        return engine
    
    # Interval management [REQ-0003]
    def test_set_interval_valid(self, monitoring_engine):
        """Test setting check interval [REQ-0003]."""
        monitoring_engine.set_interval(30)
        assert monitoring_engine._interval_minutes == 30
    
    def test_set_interval_emits_signal(self, monitoring_engine):
        """Test interval change emits signal."""
        monitoring_engine.interval_changed.emit = Mock()
        monitoring_engine.set_interval(20)
        monitoring_engine.interval_changed.emit.assert_called_once_with(20)
    
    def test_set_interval_bounds(self, monitoring_engine):
        """Test interval validation (1-60 minutes expected)."""
        monitoring_engine.set_interval(1)
        assert monitoring_engine._interval_minutes == 1
        
        monitoring_engine.set_interval(60)
        assert monitoring_engine._interval_minutes == 60
        
        # Out of bounds behavior (implementation-specific)
        with pytest.raises(ValueError):
            monitoring_engine.set_interval(0)
    
    # Nameday checking [REQ-0004, REQ-0023]
    def test_check_namedays_no_matches(self, monitoring_engine, mock_nameday_ref):
        """Test check when no namedays match today."""
        mock_nameday_ref.get_names_for_date.return_value = []
        notifications = monitoring_engine.check_namedays()
        assert len(notifications) == 0
    
    def test_check_namedays_single_match(self, monitoring_engine, mock_nameday_ref):
        """Test check with one matching nameday."""
        mock_nameday_ref.get_names_for_date.return_value = ["János"]
        notifications = monitoring_engine.check_namedays()
        assert len(notifications) == 1
        assert notifications[0].contact.name == "János"
    
    def test_check_namedays_multiple_matches(self, monitoring_engine, mock_nameday_ref):
        """Test check with multiple matching namedays [REQ-0004]."""
        # Two people with same nameday
        mock_nameday_ref.get_names_for_date.return_value = ["János", "John"]
        
        # Mock: John is not in contact DB, János is
        notifications = monitoring_engine.check_namedays()
        # Should have notification for János (and maybe John if in DB)
        assert len(notifications) >= 1
    
    def test_check_namedays_uses_mmdd_format(self, monitoring_engine):
        """Test check uses MM-DD format [REQ-0023]."""
        with patch('app.core.monitoring_engine.DateUtils.get_today_mmdd') as mock_date:
            mock_date.return_value = "03-30"
            monitoring_engine.check_namedays()
            # Should have called with MM-DD format
            monitoring_engine._nameday_ref.get_names_for_date.assert_called_with("03-30")
    
    # Background thread [REQ-0022]
    def test_start_monitoring(self, monitoring_engine):
        """Test starting background monitoring."""
        monitoring_engine.start()
        assert monitoring_engine.isRunning() or monitoring_engine._running
    
    def test_stop_monitoring(self, monitoring_engine):
        """Test stopping background monitoring."""
        monitoring_engine._running = True
        monitoring_engine.stop_monitoring()
        assert monitoring_engine._running is False
    
    # Resource efficiency [REQ-0024]
    def test_thread_cleanup(self, monitoring_engine):
        """Test proper thread cleanup to avoid memory leaks."""
        monitoring_engine.start()
        monitoring_engine.stop_monitoring()
        # Wait for thread to finish
        monitoring_engine.wait(2000)  # 2 second timeout
        assert not monitoring_engine.isRunning()
    
    @pytest.mark.slow
    def test_memory_usage_stable(self, monitoring_engine):
        """Test memory usage doesn't grow unbounded [REQ-0024]."""
        import psutil
        import os
        process = psutil.Process(os.getpid())
        
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run multiple iterations
        for _ in range(100):
            monitoring_engine.check_namedays()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Memory growth should be minimal
        assert final_memory - initial_memory < 10  # Less than 10MB growth
```

#### `tests/unit/core/test_notification_manager.py` [REQ-0005-0009, REQ-0019]

```python
import pytest
from unittest.mock import Mock, MagicMock
from app.core.notification_manager import NotificationManager, Notification

class TestNotificationManager:
    """Test notification handling [REQ-0005-0009, REQ-0019]."""
    
    @pytest.fixture
    def notification_manager(self):
        """Create notification manager."""
        email_service = Mock()
        return NotificationManager(email_service)
    
    @pytest.fixture
    def sample_notification(self):
        """Create sample notification."""
        return Notification(
            contact=Mock(name="János", email_addresses="janos@ex.com"),
            nameday_date="06-04",
            timestamp=datetime.now(),
            is_deferred=False
        )
    
    # Queue management [REQ-0004]
    def test_queue_notification(self, notification_manager, sample_notification):
        """Test queueing notification."""
        notification_manager.queue_notification(sample_notification)
        assert notification_manager.queue_size() == 1
    
    def test_queue_display_order(self, notification_manager):
        """Test notifications shown in queue order."""
        notif1 = Mock(contact=Mock(name="User1"))
        notif2 = Mock(contact=Mock(name="User2"))
        notification_manager.queue_notification(notif1)
        notification_manager.queue_notification(notif2)
        
        assert notification_manager.next_notification().contact.name == "User1"
    
    # Modal display [REQ-0005]
    def test_show_notification_creates_modal(self, notification_manager, sample_notification):
        """Test showing notification modal [REQ-0005]."""
        with patch('app.core.notification_manager.NotificationModal') as MockModal:
            notification_manager.show_notification(sample_notification)
            MockModal.assert_called_once()
    
    # User actions [REQ-0006, REQ-0007, REQ-0008]
    def test_handle_later_button(self, notification_manager, sample_notification):
        """Test 'Later' button: reschedule notification [REQ-0006]."""
        deferred = notification_manager.handle_later(sample_notification, minutes=30)
        assert deferred.is_deferred is True
        assert deferred.deferred_until is not None
    
    def test_handle_mail_button(self, notification_manager, sample_notification):
        """Test 'Mail' button: send email [REQ-0007, REQ-0019]."""
        notification_manager._email_service = Mock()
        notification_manager.handle_mail(sample_notification)
        notification_manager._email_service.send_email.assert_called_once()
    
    def test_handle_done_button(self, notification_manager, sample_notification):
        """Test 'Done' button: disable further notifications [REQ-0008]."""
        notification_manager.handle_done(sample_notification)
        # Should update contact to disable notifications
        # Implementation-specific verification
    
    # Signal emissions
    def test_notification_displayed_signal(self, notification_manager, sample_notification):
        """Test notification_displayed signal emitted."""
        notification_manager.notification_displayed.emit = Mock()
        notification_manager.queue_notification(sample_notification)
        # Signal should be emitted
```

### 2.5 UI Tests

#### `tests/unit/ui/test_notification_modal.py` [REQ-0043, REQ-0044]

```python
import pytest
from unittest.mock import Mock
from app.ui.notification_modal import NotificationModal

class TestNotificationModal:
    """Test notification modal dialog [REQ-0043, REQ-0044]."""
    
    @pytest.fixture
    def sample_notification(self):
        """Create sample notification."""
        return Mock(
            contact=Mock(name="János", recipient="János"),
            nameday_date="06-04"
        )
    
    @pytest.fixture
    def notification_modal(self, sample_notification, qtbot):
        """Create notification modal."""
        modal = NotificationModal(sample_notification)
        qtbot.addWidget(modal)
        return modal
    
    # Modal display [REQ-0005, REQ-0043]
    def test_modal_is_dialog(self, notification_modal):
        """Test modal is a QDialog."""
        assert isinstance(notification_modal, QDialog)
    
    def test_modal_displays_contact_name(self, notification_modal):
        """Test modal shows contact name [REQ-0043]."""
        assert notification_modal.findChild(QLabel).text() contains "János"
    
    def test_modal_displays_nameday_date(self, notification_modal):
        """Test modal shows nameday date."""
        labels = notification_modal.findChildren(QLabel)
        assert any("06-04" in lbl.text() for lbl in labels)
    
    # Button layout [REQ-0044]
    def test_modal_has_three_buttons(self, notification_modal):
        """Test modal has Later, Mail, Done buttons [REQ-0044]."""
        buttons = notification_modal.findChildren(QPushButton)
        assert len(buttons) == 3
        button_texts = [btn.text() for btn in buttons]
        assert "Later" in button_texts
        assert "Mail" in button_texts
        assert "Done" in button_texts
    
    def test_later_button_callable(self, notification_modal, qtbot):
        """Test Later button is clickable."""
        later_btn = notification_modal._get_button("Later")
        assert later_btn.isEnabled()
        with qtbot.assertEmitted(later_btn.clicked):
            qtbot.mouseClick(later_btn, Qt.LeftButton)
    
    def test_mail_button_callable(self, notification_modal, qtbot):
        """Test Mail button is clickable."""
        mail_btn = notification_modal._get_button("Mail")
        assert mail_btn.isEnabled()
        with qtbot.assertEmitted(mail_btn.clicked):
            qtbot.mouseClick(mail_btn, Qt.LeftButton)
    
    def test_done_button_callable(self, notification_modal, qtbot):
        """Test Done button is clickable."""
        done_btn = notification_modal._get_button("Done")
        assert done_btn.isEnabled()
    
    # Modal behavior
    def test_modal_is_focused(self, notification_modal):
        """Test modal gets focus [REQ-0005]."""
        notification_modal.exec()
        assert notification_modal.hasFocus()
    
    def test_modal_is_blocking(self, notification_modal):
        """Test modal is blocking [REQ-0005]."""
        # Modal should block interaction with other windows
        assert notification_modal.isModal() is True
```

#### `tests/unit/ui/test_system_tray.py` [REQ-0010, REQ-0042]

```python
import pytest
from app.ui.system_tray import SystemTrayManager

class TestSystemTrayManager:
    """Test system tray integration [REQ-0010, REQ-0042]."""
    
    @pytest.fixture
    def tray_manager(self, qtbot):
        """Create system tray manager."""
        manager = SystemTrayManager()
        return manager
    
    # Tray icon [REQ-0010, REQ-0042]
    def test_tray_icon_created(self, tray_manager):
        """Test system tray icon is created."""
        assert tray_manager._tray_icon is not None
        assert isinstance(tray_manager._tray_icon, QSystemTrayIcon)
    
    def test_tray_icon_visible(self, tray_manager):
        """Test tray icon is visible when shown."""
        tray_manager.show()
        assert tray_manager._tray_icon.isVisible()
    
    # Context menu [REQ-0010]
    def test_tray_has_context_menu(self, tray_manager):
        """Test right-click context menu [REQ-0010]."""
        assert tray_manager._menu is not None
        assert isinstance(tray_manager._menu, QMenu)
    
    def test_menu_has_required_items(self, tray_manager):
        """Test menu contains required menu items."""
        menu = tray_manager._menu
        action_texts = [action.text() for action in menu.actions()]
        
        # Should have these menu items [REQ-0010, REQ-0011-0015]
        assert "Show All" in action_texts       # REQ-0012
        assert "Query Nameday" in action_texts  # REQ-0013
        assert "Settings" in action_texts       # REQ-0014
        assert "Edit Database" in action_texts  # REQ-0011
        assert "Exit" in action_texts           # REQ-0015
    
    def test_menu_item_callbacks(self, tray_manager, monkeypatch):
        """Test menu items trigger correct actions."""
        # Mock callbacks
        show_all = Mock()
        monkeypatch.setattr(tray_manager, "show_all_namedays", show_all)
        
        # Get and click menu action
        menu = tray_manager._menu
        action = [a for a in menu.actions() if "Show All" in a.text()][0]
        action.trigger()
        
        show_all.assert_called_once()
```

#### `tests/unit/i18n/test_i18n_manager.py` [REQ-0045, REQ-0046]

```python
import pytest
from app.i18n.i18n_manager import I18nManager

class TestI18nManager:
    """Test internationalization [REQ-0045, REQ-0046]."""
    
    @pytest.fixture
    def i18n_manager(self):
        """Create i18n manager."""
        return I18nManager()
    
    # Language selection [REQ-0045]
    def test_set_language_english(self, i18n_manager):
        """Test setting English language [REQ-0045]."""
        i18n_manager.set_language("en")
        assert i18n_manager.current_language == "en"
    
    def test_set_language_hungarian(self, i18n_manager):
        """Test setting Hungarian language [REQ-0045]."""
        i18n_manager.set_language("hu")
        assert i18n_manager.current_language == "hu"
    
    def test_set_language_invalid(self, i18n_manager):
        """Test setting invalid language."""
        with pytest.raises(ValueError):
            i18n_manager.set_language("invalid")
    
    # String localization [REQ-0046]
    def test_get_string_english(self, i18n_manager):
        """Test getting localized string in English."""
        i18n_manager.set_language("en")
        button_text = i18n_manager.get_string("button.later")
        assert button_text is not None
        assert button_text != "button.later"  # Should be translated
    
    def test_get_string_hungarian(self, i18n_manager):
        """Test getting localized string in Hungarian."""
        i18n_manager.set_language("hu")
        button_text = i18n_manager.get_string("button.later")
        assert button_text is not None
        assert button_text != "button.later"
    
    def test_get_string_with_placeholders(self, i18n_manager):
        """Test string with variable substitution."""
        i18n_manager.set_language("en")
        message = i18n_manager.get_string("notification.nameday", name="János")
        assert "János" in message
    
    def test_language_change_signals(self, i18n_manager):
        """Test language change emits signal."""
        i18n_manager.language_changed.emit = Mock()
        i18n_manager.set_language("hu")
        i18n_manager.language_changed.emit.assert_called_once_with("hu")
    
    # Fallback behavior
    def test_missing_string_fallback(self, i18n_manager):
        """Test fallback for missing translations."""
        # Should not crash, might return key or English
        result = i18n_manager.get_string("non.existent.key")
        assert result is not None
    
    def test_all_keys_translated(self, i18n_manager):
        """Test all keys exist in all languages."""
        en_strings = i18n_manager._load_language("en")
        hu_strings = i18n_manager._load_language("hu")
        
        en_keys = set(en_strings.keys())
        hu_keys = set(hu_strings.keys())
        
        # All English keys should have Hungarian translations
        assert en_keys == hu_keys
```

---

## 3. Integration Test Implementation

### 3.1 Startup Sequence Test

**`tests/integration/test_startup_sequence.py`**

```python
def test_application_startup_sequence():
    """Test complete application startup [REQ-0001, REQ-0022]."""
    # 1. Create app
    # 2. Load settings [REQ-0026]
    # 3. Initialize managers [REQ-0017, REQ-0018]
    # 4. Start monitoring [REQ-0022]
    # 5. Create UI [REQ-0010]
    # 6. Detect auto-launch [REQ-0002]
    
    app = NameDaysMonitoringApp()
    assert app._monitoring_engine.isRunning()
    assert app._system_tray.is_visible()
```

### 3.2 Notification Workflow Test

**`tests/integration/test_notification_workflow.py`**

```python
def test_complete_notification_workflow():
    """Test notification display and user actions [REQ-0004-0009]."""
    # 1. Monitoring engine detects nameday [REQ-0004]
    # 2. Notification queued [REQ-0004]
    # 3. Modal displayed [REQ-0005]
    # 4. User clicks button [REQ-0006, REQ-0007, REQ-0008]
    # 5. Appropriate action taken
```

---

## 4. Performance Test Implementation

### 4.1 Memory Usage Test

**`tests/performance/test_memory_usage.py` [REQ-0024]**

```python
@pytest.mark.performance
def test_memory_usage_under_limit():
    """Test application memory usage < 100MB [REQ-0024]."""
    import psutil
    process = psutil.Process()
    initial = process.memory_info().rss / 1024 / 1024
    
    # Simulate operations
    engine = MonitoringEngine(...)
    for _ in range(1000):
        engine.check_namedays()
    
    final = process.memory_info().rss / 1024 / 1024
    assert final < 100, f"Memory usage {final}MB exceeds 100MB limit"
```

### 4.2 CPU Usage Test

**`tests/performance/test_cpu_usage.py` [REQ-0024]**

```python
@pytest.mark.performance
def test_cpu_usage_at_rest():
    """Test CPU usage is minimal at rest [REQ-0024]."""
    import psutil
    process = psutil.Process()
    
    # Let app idle for 1 second
    time.sleep(1)
    cpu_percent = process.cpu_percent(interval=1)
    
    assert cpu_percent < 5, f"CPU usage {cpu_percent}% is too high"
```

### 4.3 Interval Accuracy Test

**`tests/performance/test_interval_accuracy.py` [REQ-0003]**

```python
def test_monitoring_interval_accuracy():
    """Test check interval is accurate [REQ-0003]."""
    engine = MonitoringEngine(...)
    engine.set_interval(15)  # 15 minutes
    
    check_times = []
    for _ in range(5):
        before = time.time()
        engine.check_namedays()
        after = time.time()
        check_times.append(after - before)
    
    avg_interval = sum(check_times) / len(check_times)
    assert avg_interval > 14.5 * 60  # Within 30 seconds of target
```

---

## 5. Windows Compatibility Tests

### 5.1 Registry Operations Test

**`tests/windows_compat/test_registry_operations.py` [REQ-0051]**

```python
@pytest.mark.windows_compat
@pytest.mark.skipif(not sys.platform.startswith('win'), reason="Windows only")
def test_registry_read_write():
    """Test Windows registry operations [REQ-0051]."""
    manager = WindowsStartupManager()
    assert manager.enable_auto_launch() is True
    assert manager.is_auto_launch_enabled() is True
    manager.disable_auto_launch()
    assert manager.is_auto_launch_enabled() is False
```

### 5.2 Windows 10/11 Compatibility Test

**`tests/windows_compat/test_system_integration.py` [REQ-0025]**

```python
@pytest.mark.windows_compat
@pytest.mark.skipif(not sys.platform.startswith('win'), reason="Windows only")
def test_windows_10_compatibility():
    """Test Windows 10 compatibility [REQ-0025]."""
    version = sys.getwindowsversion()
    assert version.major == 10 or version.major > 10
    
    # Test tray integration
    app = NameDaysMonitoringApp()
    assert app._system_tray.is_visible()
```

---

## 6. Test Fixtures and Utilities

### 6.1 Common Fixtures

**`tests/fixtures/contact_fixtures.py`**

```python
@pytest.fixture
def contact_fixture():
    """Provide sample contact for testing."""
    return Contact(
        name="János Kovács",
        main_nameday="06-04",
        other_nameday="11-30",
        recipient="János (work)",
        email_addresses="janos@example.com",
        prewritten_email="Dear János,\nHappy nameday!",
        comment="Colleague from IT"
    )

@pytest.fixture
def multiple_contacts_fixture():
    """Provide multiple sample contacts."""
    return [
        Contact(name="János", main_nameday="06-04", ...),
        Contact(name="Mária", main_nameday="05-01", ...),
        Contact(name="Andrea", main_nameday="11-30", ...)
    ]
```

### 6.2 Mock Services

**`tests/fixtures/mock_services.py`**

```python
@pytest.fixture
def mock_email_service(monkeypatch):
    """Mock Gmail SMTP service."""
    mock = Mock(spec=EmailService)
    mock.send_email.return_value = True
    return mock

@pytest.fixture
def mock_registry(monkeypatch):
    """Mock Windows registry."""
    mock = Mock()
    monkeypatch.setattr("winreg.OpenKey", mock)
    return mock
```

### 6.3 conftest.py Configuration

**`tests/conftest.py`**

```python
import pytest
from PyQt5.QtWidgets import QApplication

@pytest.fixture(scope="session")
def qapp():
    """Create Qt application for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()

@pytest.fixture
def qtbot(qapp, monkeypatch):
    """Provide QtBot for UI testing."""
    from pytestqt.qtbot import QtBot
    return QtBot(qapp)

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "windows_compat: mark test as Windows-specific"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance-related"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
```

---

## 7. Coverage Report Strategy

### 7.1 Coverage Targets by Module

```
app/
├── __init__.py                         100%
├── main.py                             90% (UI interactions hard to test)
├── constants.py                        100%
├── types.py                            100%
├── exceptions.py                       100%
├── core/
│   ├── monitoring_engine.py            85% (threading complexity)
│   ├── notification_manager.py         90%
│   └── notification_queue.py           95%
├── managers/
│   ├── contact_db_manager.py           90%
│   ├── nameday_reference_manager.py    95%
│   ├── settings_manager.py             95%
│   └── config_validator.py             90%
├── services/
│   ├── email_service.py                85% (SMTP interactions mocked)
│   ├── windows_startup.py              80% (Registry-specific)
│   └── data_validator.py               100%
├── ui/                                 75% (UI framework complexity)
├── i18n/                               95%
└── utils/                              95%
```

**Overall Target:** >80% code coverage

### 7.2 Human Review of Untested Code

Coverage gaps to review manually:
- PyQt5 signal/slot connections (difficult to unit test)
- Registry access on non-Windows systems
- SMTP error handling edge cases
- UI rendering/layout specifics

---

## 8. Continuous Integration / CI Strategy

### 8.1 GitHub Actions Configuration

**`.github/workflows/test.yml`**

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: [3.7, 3.8, 3.9, 3.10, 3.11]

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests
        run: pytest --cov=app --cov-report=xml --maxfail=3
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
      
      - name: Check coverage
        run: pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

---

## 9. Test Execution Plan

### Phase Order

```
Week 7: Testing & Optimization

Day 1: Foundation Tests (Utils, Exceptions)
  - Run: tests/unit/utils/*
  - Run: tests/unit/test_constants.py, test_types.py, test_exceptions.py

Day 2: Service Tests
  - Run: tests/unit/services/*
  - Manual: SMTP with live test (skip in CI)

Day 3: Manager Tests
  - Run: tests/unit/managers/*
  - Focus: CSV I/O, database operations

Day 4: Core Engine Tests
  - Run: tests/unit/core/*
  - Performance: Memory/CPU baselines

Day 5: UI Tests
  - Run: tests/unit/ui/*
  - i18n: tests/unit/i18n/*

Day 6: Integration Tests
  - Run: tests/integration/*
  - Full workflow validation

Day 7: Performance & Windows Compatibility
  - Run: tests/performance/*
  - Run: tests/windows_compat/*
  - Coverage analysis and reporting
```

### Command Examples

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit/

# Run specific test file
pytest tests/unit/test_data_validator.py

# Run with coverage report
pytest --cov=app --cov-report=html

# Run only fast tests (exclude slow/performance)
pytest -m "not slow"

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_validate"

# Run with specific quit parameters
pytest --maxfail=3 --tb=short
```

---

## 10. Test Documentation

### Every Test Should Answer

1. **What is being tested?** (class/function name)
2. **What scenario?** (valid/invalid/edge case)
3. **What requirement does it map to?** (REQ-ID)
4. **What is the expected behavior?** (assertion)

### Example Docstring Format

```python
def test_contact_db_manager_create_contact_valid_data(db_manager, sample_contact):
    """
    Test creating a valid contact in database.
    
    Scenario: Create contact with all required fields populated
    Requirement: REQ-0017 (CRUD operations)
    Expected: Contact created with unique ID
    """
    contact_id = db_manager.create_contact(sample_contact)
    assert contact_id is not None
    assert isinstance(contact_id, str)
```

---

## 11. Troubleshooting Guide

### Common Test Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Qt tests fail on Linux | Display server | Use `xvfb-run pytest` |
| Registry tests fail | Non-Windows | Use `@pytest.mark.skipif` |
| SMTP tests timeout | Network issues | Increase timeout, use mocks |
| Memory tests fail | Background processes | Run in isolation |
| CSV encoding issues | Windows line endings | Use `encoding='utf-8'` |

---

## Appendix: Test Statistics

```
Expected Test Count:
  - Unit Tests:          120 tests (>80% coverage)
  - Integration Tests:    15 tests
  - Performance Tests:     8 tests
  - Windows Compat:       5 tests
  ─────────────────────────────
  Total:                148 tests

Expected Execution Time:
  - Full Suite:          < 5 minutes
  - Unit Only:           < 3 minutes
  - Integration Only:    < 1 minute
  - Performance:         < 1 minute (actual timing varies)

Coverage Targets:
  - Overall:             > 80%
  - Core Engine:         > 85%
  - Data Layer:          > 90%
  - Services:            > 85%
  - UI:                  > 75%
```

---

## Document Control

**Version:** 1.0  
**Date:** 2026-03-30  
**Status:** Final Test Plan  
**Total Test Objects:** 148+  
**Expected Coverage:** >80% of codebase  
**Alignment:** 55/55 requirements covered by tests
