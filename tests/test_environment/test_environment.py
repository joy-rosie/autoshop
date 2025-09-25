import os
import tempfile
from pathlib import Path

import pytest

from autoshop import all as autoshop


# Tests for environment.get function
def test_get_existing_key(mocker):
    """Test getting an existing environment variable."""
    mock_env_data = {"TEST_KEY": "test_value", "ANOTHER_KEY": "another_value"}

    mocker.patch("autoshop.environment.dotenv_values", return_value=mock_env_data)
    result = autoshop.env.get("TEST_KEY")
    assert result == "test_value"


def test_get_nonexistent_key_raises_keyerror(mocker):
    """Test that getting a nonexistent key raises KeyError."""
    mock_env_data = {"EXISTING_KEY": "value"}

    mocker.patch("autoshop.environment.dotenv_values", return_value=mock_env_data)
    with pytest.raises(KeyError):
        autoshop.env.get("NONEXISTENT_KEY")


def test_get_with_custom_path(mocker):
    """Test getting environment variables from a custom path."""
    custom_path = Path("/custom/path/.env")
    mock_env_data = {"CUSTOM_KEY": "custom_value"}

    mock_dotenv = mocker.patch(
        "autoshop.environment.dotenv_values", return_value=mock_env_data
    )
    result = autoshop.env.get("CUSTOM_KEY", path=custom_path)

    assert result == "custom_value"
    mock_dotenv.assert_called_with(dotenv_path=custom_path)


def test_get_with_numeric_values(mocker):
    """Test that numeric values are preserved."""
    mock_env_data = {"STRING_VAL": "text", "INT_VAL": 42, "FLOAT_VAL": 3.14}

    mocker.patch("autoshop.environment.dotenv_values", return_value=mock_env_data)
    # Clear cache to ensure fresh load
    autoshop.env.get_environment_variables.cache_clear()

    assert autoshop.env.get("STRING_VAL") == "text"
    assert autoshop.env.get("INT_VAL") == 42
    assert autoshop.env.get("FLOAT_VAL") == 3.14


# Tests for get_environment_variables function
def test_get_environment_variables_default_path(mocker):
    """Test loading environment variables from default path."""
    mock_env_data = {"KEY1": "value1", "KEY2": "value2"}

    mock_dotenv = mocker.patch(
        "autoshop.environment.dotenv_values", return_value=mock_env_data
    )
    result = autoshop.env.get_environment_variables()

    assert result == mock_env_data
    # Should use the default path (relative to the module)
    expected_path = Path(autoshop.env.__file__).parents[1] / ".env"
    mock_dotenv.assert_called_with(dotenv_path=expected_path)


def test_get_environment_variables_custom_path(mocker):
    """Test loading environment variables from custom path."""
    custom_path = Path("/tmp/custom.env")
    mock_env_data = {"CUSTOM": "data"}

    mock_dotenv = mocker.patch(
        "autoshop.environment.dotenv_values", return_value=mock_env_data
    )
    result = autoshop.env.get_environment_variables(path=custom_path)

    assert result == mock_env_data
    mock_dotenv.assert_called_with(dotenv_path=custom_path)


def test_get_environment_variables_caching(mocker):
    """Test that environment variables are cached."""
    mock_env_data = {"CACHED": "value"}

    mock_dotenv = mocker.patch(
        "autoshop.environment.dotenv_values", return_value=mock_env_data
    )
    # Clear the cache first
    autoshop.env.get_environment_variables.cache_clear()

    # First call
    result1 = autoshop.env.get_environment_variables()

    # Second call should use cache
    result2 = autoshop.env.get_environment_variables()

    assert result1 == result2 == mock_env_data
    # dotenv_values should only be called once due to caching
    assert mock_dotenv.call_count == 1


# Integration tests with actual .env files
def test_with_real_env_file():
    """Test with a real temporary .env file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("TEST_VAR=test_value\n")
        f.write("NUMBER_VAR=123\n")
        f.write("FLOAT_VAR=45.67\n")
        temp_path = Path(f.name)

    try:
        # Clear cache to ensure fresh load
        autoshop.env.get_environment_variables.cache_clear()

        result = autoshop.env.get_environment_variables(path=temp_path)

        assert "TEST_VAR" in result
        assert result["TEST_VAR"] == "test_value"
        # Note: dotenv_values returns strings, not parsed numbers
        assert result["NUMBER_VAR"] == "123"
        assert result["FLOAT_VAR"] == "45.67"

        # Test the get function as well
        assert autoshop.env.get("TEST_VAR", path=temp_path) == "test_value"

    finally:
        # Clean up
        os.unlink(temp_path)


def test_with_empty_env_file():
    """Test with an empty .env file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        temp_path = Path(f.name)

    try:
        # Clear cache to ensure fresh load
        autoshop.env.get_environment_variables.cache_clear()

        result = autoshop.env.get_environment_variables(path=temp_path)

        assert result == {}

    finally:
        # Clean up
        os.unlink(temp_path)


def test_with_nonexistent_file():
    """Test with a nonexistent .env file."""
    nonexistent_path = Path("/definitely/does/not/exist/.env")

    # Clear cache to ensure fresh load
    autoshop.env.get_environment_variables.cache_clear()

    # Should handle gracefully (dotenv_values returns empty dict for missing files)
    result = autoshop.env.get_environment_variables(path=nonexistent_path)
    assert result == {}


# Tests for environment module constants
def test_default_path_constant():
    """Test that the default path constant is correctly defined."""
    expected_path = Path(autoshop.env.__file__).parents[1] / ".env"
    assert autoshop.env.PATH_DOTENV_DEFAULT == expected_path


def test_logger_exists():
    """Test that the logger is properly initialized."""
    assert hasattr(autoshop.env, "LOGGER")
    assert autoshop.env.LOGGER is not None


# Edge cases and error conditions
def test_get_with_none_path_uses_default(mocker):
    """Test that passing None as path uses the default."""
    mock_env_data = {"DEFAULT": "value"}

    mock_dotenv = mocker.patch(
        "autoshop.environment.dotenv_values", return_value=mock_env_data
    )
    # Clear cache
    autoshop.env.get_environment_variables.cache_clear()

    result = autoshop.env.get("DEFAULT", path=None)

    assert result == "value"
    expected_path = Path(autoshop.env.__file__).parents[1] / ".env"
    mock_dotenv.assert_called_with(dotenv_path=expected_path)


def test_type_annotations():
    """Test that the TYPE_ENVIRONMENT_VALUE type hint is properly defined."""
    # This is more of a static check, but we can verify the constant exists
    assert hasattr(autoshop.env, "TYPE_ENVIRONMENT_VALUE")


def test_multiple_different_paths_cached_separately(mocker):
    """Test that different paths are cached separately."""
    path1 = Path("/path1/.env")
    path2 = Path("/path2/.env")
    mock_data1 = {"PATH1": "data1"}
    mock_data2 = {"PATH2": "data2"}

    mock_dotenv = mocker.patch(
        "autoshop.environment.dotenv_values", side_effect=[mock_data1, mock_data2]
    )
    # Clear cache
    autoshop.env.get_environment_variables.cache_clear()

    result1 = autoshop.env.get_environment_variables(path=path1)
    result2 = autoshop.env.get_environment_variables(path=path2)

    assert result1 == mock_data1
    assert result2 == mock_data2
    assert mock_dotenv.call_count == 2
