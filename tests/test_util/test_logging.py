import logging
import os
import sys
import tempfile

import pytest

from autoshop.util import logging as autoshop_logging


# Tests for the logging formatter
def test_formatter_exists():
    """Test that the formatter is properly defined."""
    assert hasattr(autoshop_logging, "FORMATTER")
    assert isinstance(autoshop_logging.FORMATTER, logging.Formatter)


def test_formatter_format():
    """Test the formatter format string."""
    formatter = autoshop_logging.FORMATTER

    # Create a test log record
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_path.py",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None,
        func="test_function",
    )

    formatted = formatter.format(record)

    # Check that expected components are in the formatted string
    assert "INFO" in formatted
    assert "test message" in formatted.lower()
    assert "test_function" in formatted
    # The formatter uses %(module)s, not %(name)s, so it shows the module name
    assert "test_logging" in formatted or "test_path" in formatted


# Tests for the file handler configuration
def test_file_handler_exists():
    """Test that the file handler is properly configured."""
    assert hasattr(autoshop_logging, "FILE_HANDLER")
    assert isinstance(autoshop_logging.FILE_HANDLER, logging.FileHandler)


def test_file_handler_level():
    """Test that file handler has DEBUG level."""
    assert autoshop_logging.FILE_HANDLER.level == logging.DEBUG


def test_file_handler_formatter():
    """Test that file handler uses the correct formatter."""
    assert autoshop_logging.FILE_HANDLER.formatter == autoshop_logging.FORMATTER


def test_file_handler_filename():
    """Test that file handler uses correct filename."""
    expected_filename = "autoshop.log"
    # The baseFilename attribute contains the full path, so check if it ends with our expected name
    assert autoshop_logging.FILE_HANDLER.baseFilename.endswith(expected_filename)


# Tests for the console handler configuration
def test_console_handler_exists():
    """Test that the console handler is properly configured."""
    assert hasattr(autoshop_logging, "CONSOLE_HANDLER")
    assert isinstance(autoshop_logging.CONSOLE_HANDLER, logging.StreamHandler)


def test_console_handler_level():
    """Test that console handler has INFO level."""
    assert autoshop_logging.CONSOLE_HANDLER.level == logging.INFO


def test_console_handler_formatter():
    """Test that console handler uses the correct formatter."""
    assert autoshop_logging.CONSOLE_HANDLER.formatter == autoshop_logging.FORMATTER


def test_console_handler_stream():
    """Test that console handler writes to stdout."""
    import sys

    assert autoshop_logging.CONSOLE_HANDLER.stream == sys.stdout


# Tests for the logger factory function
def test_logger_returns_logger_instance():
    """Test that logger function returns a Logger instance."""
    test_logger = autoshop_logging.logger("test_name")
    assert isinstance(test_logger, logging.Logger)


def test_logger_has_correct_name():
    """Test that logger has the correct name."""
    name = "test_logger_name"
    test_logger = autoshop_logging.logger(name)
    assert test_logger.name == name


def test_logger_has_file_handler():
    """Test that logger includes the file handler."""
    test_logger = autoshop_logging.logger("test_with_file")
    handlers = test_logger.handlers

    # Should have both file and console handlers
    assert len(handlers) == 2

    # Check that one of them is the file handler
    file_handlers = [h for h in handlers if isinstance(h, logging.FileHandler)]
    assert len(file_handlers) == 1
    assert file_handlers[0] == autoshop_logging.FILE_HANDLER


def test_logger_has_console_handler():
    """Test that logger includes the console handler."""
    test_logger = autoshop_logging.logger("test_with_console")
    handlers = test_logger.handlers

    # Check that one of them is the console handler
    console_handlers = [
        h
        for h in handlers
        if isinstance(h, logging.StreamHandler)
        and not isinstance(h, logging.FileHandler)
    ]
    assert len(console_handlers) == 1
    assert console_handlers[0] == autoshop_logging.CONSOLE_HANDLER


def test_multiple_loggers_different_names():
    """Test creating multiple loggers with different names."""
    logger1 = autoshop_logging.logger("logger1")
    logger2 = autoshop_logging.logger("logger2")

    assert logger1.name != logger2.name
    assert logger1.name == "logger1"
    assert logger2.name == "logger2"

    # Both should have the same handlers
    assert len(logger1.handlers) == len(logger2.handlers) == 2


# Tests for actual logging functionality
def test_logger_logs_to_console():
    """Test that logger has console handler configured correctly."""
    test_logger = autoshop_logging.logger("console_test")

    # Check that the logger has the expected handlers
    assert len(test_logger.handlers) == 2

    # Find the console handler
    console_handler = None
    for handler in test_logger.handlers:
        if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
            console_handler = handler
            break

    assert console_handler is not None
    assert console_handler.level == logging.INFO

    # Test that INFO level messages would be handled
    assert test_logger.isEnabledFor(logging.INFO)
    assert console_handler.level <= logging.INFO


def test_logger_debug_not_on_console():
    """Test that DEBUG messages don't appear on console (INFO level)."""
    test_logger = autoshop_logging.logger("debug_test")

    # Find the console handler
    console_handler = None
    for handler in test_logger.handlers:
        if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
            console_handler = handler
            break

    assert console_handler is not None
    assert console_handler.level == logging.INFO

    # DEBUG messages should not be handled by console (level is INFO)
    assert console_handler.level > logging.DEBUG


def test_logger_error_on_console():
    """Test that ERROR messages appear on console."""
    test_logger = autoshop_logging.logger("error_test")

    # Find the console handler
    console_handler = None
    for handler in test_logger.handlers:
        if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
            console_handler = handler
            break

    assert console_handler is not None
    assert console_handler.level == logging.INFO

    # ERROR messages should be handled by console (ERROR > INFO)
    assert console_handler.level <= logging.ERROR
    assert test_logger.isEnabledFor(logging.ERROR)


@pytest.mark.integration
def test_logger_writes_to_file():
    """Test that logger writes to file. This is an integration test."""

    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".log", delete=False
    ) as temp_file:
        temp_path = temp_file.name

    try:
        # Create a custom file handler for this test
        test_file_handler = logging.FileHandler(temp_path, mode="a")
        test_file_handler.setLevel(logging.DEBUG)
        test_file_handler.setFormatter(autoshop_logging.FORMATTER)

        # Create a logger with our test file handler
        test_logger = logging.Logger("file_test")
        test_logger.addHandler(test_file_handler)

        # Log some messages
        test_logger.debug("Debug message for file")
        test_logger.info("Info message for file")
        test_logger.error("Error message for file")

        # Close the handler to flush
        test_file_handler.close()

        # Read the file and verify contents
        with open(temp_path, "r") as f:
            content = f.read()

        assert "Debug message for file" in content
        assert "Info message for file" in content
        assert "Error message for file" in content
        assert "DEBUG" in content
        assert "INFO" in content
        assert "ERROR" in content

    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)


# Tests for logging module constants
def test_filename_constant():
    """Test the FILENAME constant."""
    assert autoshop_logging.FILENAME == "autoshop.log"


def test_formatter_datefmt():
    """Test the formatter date format."""
    formatter = autoshop_logging.FORMATTER
    assert formatter.datefmt == "%Y-%m-%d %H:%M:%S"


def test_all_exports():
    """Test that __all__ contains expected exports."""
    assert hasattr(autoshop_logging, "__all__")
    assert "logger" in autoshop_logging.__all__


# Integration tests for the logging module
def test_autoshop_main_logger():
    """Test that the main autoshop logger works correctly."""
    # This tests the logger as it would be used in the main module

    # The main module creates a logger like this
    main_logger = autoshop_logging.logger("autoshop")

    # Test that it has the right configuration
    assert len(main_logger.handlers) == 2
    assert main_logger.isEnabledFor(logging.INFO)

    # Find the console handler
    console_handler = None
    for handler in main_logger.handlers:
        if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
            console_handler = handler
            break

    assert console_handler is not None
    assert console_handler.level == logging.INFO


def test_multiple_logger_calls_same_name():
    """Test calling logger function multiple times with same name."""
    logger1 = autoshop_logging.logger("same_name")
    logger2 = autoshop_logging.logger("same_name")

    # They should be different Logger instances (not cached)
    # but have the same name
    assert logger1.name == logger2.name == "same_name"
    # In this implementation, they would be different instances
    # since the function creates a new Logger each time
