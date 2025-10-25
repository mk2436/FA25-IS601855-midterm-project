"""
tests/test_config.py

Unit tests for the CalculatorConfig class.

These tests verify:
- Correct application of environment variable overrides.
- Explicit constructor parameters overriding both defaults and environment values.
- Proper resolution of directory and file path properties.
- Validation logic that raises ConfigurationError for invalid configuration.
- Correct parsing of boolean environment values for auto_save.
- Proper default fallback behavior when environment variables are absent.
- Accurate detection of the project root directory.
"""

import pytest
import os
from decimal import Decimal
from pathlib import Path
from app.calculator_config import CalculatorConfig
from app.exceptions import ConfigurationError

# ----------------------------------------------------------------------
# ENVIRONMENT VARIABLE SETUP
# ----------------------------------------------------------------------
# These environment variables simulate system-level or user-defined overrides.
# CalculatorConfig should read and apply these values when instantiated.
# ----------------------------------------------------------------------
os.environ['CALCULATOR_MAX_HISTORY_SIZE'] = '500'
os.environ['CALCULATOR_AUTO_SAVE'] = 'false'
os.environ['CALCULATOR_PRECISION'] = '8'
os.environ['CALCULATOR_MAX_INPUT_VALUE'] = '1000'
os.environ['CALCULATOR_DEFAULT_ENCODING'] = 'utf-16'
os.environ['CALCULATOR_LOG_DIR'] = './test_logs'
os.environ['CALCULATOR_HISTORY_DIR'] = './test_history'
os.environ['CALCULATOR_HISTORY_FILE'] = './test_history/test_history.csv'
os.environ['CALCULATOR_LOG_FILE'] = './test_logs/test_log.log'


# ----------------------------------------------------------------------
# Helper: clear_env_vars
# ----------------------------------------------------------------------
# Removes specified environment variables between tests to prevent cross-test
# contamination. This ensures each test runs in a clean, predictable environment.
# ----------------------------------------------------------------------
def clear_env_vars(*args):
    for var in args:
        os.environ.pop(var, None)


# ----------------------------------------------------------------------
# TEST: Default configuration from environment
# ----------------------------------------------------------------------
# Verifies that CalculatorConfig correctly reads configuration values from
# environment variables when no explicit constructor arguments are provided.
# ----------------------------------------------------------------------
def test_default_configuration():
    config = CalculatorConfig()
    assert config.max_history_size == 500
    assert config.auto_save is False
    assert config.precision == 8
    assert config.max_input_value == Decimal("1000")
    assert config.default_encoding == 'utf-16'
    assert config.log_dir == Path('./test_logs').resolve()
    assert config.history_dir == Path('./test_history').resolve()
    assert config.history_file == Path('./test_history/test_history.csv').resolve()
    assert config.log_file == Path('./test_logs/test_log.log').resolve()


# ----------------------------------------------------------------------
# TEST: Custom configuration parameters
# ----------------------------------------------------------------------
# Ensures that explicitly passed constructor arguments override both defaults
# and environment variables.
# ----------------------------------------------------------------------
def test_custom_configuration():
    config = CalculatorConfig(
        max_history_size=300,
        auto_save=True,
        precision=5,
        max_input_value=Decimal("500"),
        default_encoding="ascii"
    )
    assert config.max_history_size == 300
    assert config.auto_save is True
    assert config.precision == 5
    assert config.max_input_value == Decimal("500")
    assert config.default_encoding == "ascii"


# ----------------------------------------------------------------------
# TEST: Directory property helpers
# ----------------------------------------------------------------------
# Checks that when log/history directories are not defined via environment
# variables, CalculatorConfig constructs them under the given base_dir.
# ----------------------------------------------------------------------
def test_directory_properties():
    clear_env_vars('CALCULATOR_LOG_DIR', 'CALCULATOR_HISTORY_DIR')
    config = CalculatorConfig(base_dir=Path('/custom_base_dir'))
    assert config.log_dir == Path('/custom_base_dir/logs').resolve()
    assert config.history_dir == Path('/custom_base_dir/history').resolve()


# ----------------------------------------------------------------------
# TEST: File property helpers
# ----------------------------------------------------------------------
# Ensures that default log and history file paths are correctly generated under
# base_dir when no environment variables are provided.
# ----------------------------------------------------------------------
def test_file_properties():
    clear_env_vars('CALCULATOR_HISTORY_FILE', 'CALCULATOR_LOG_FILE')
    config = CalculatorConfig(base_dir=Path('/custom_base_dir'))
    assert config.history_file == Path('/custom_base_dir/history/calculator_history.csv').resolve()
    assert config.log_file == Path('/custom_base_dir/logs/calculator.log').resolve()


# ----------------------------------------------------------------------
# TEST: Validation errors
# ----------------------------------------------------------------------
# Exercises CalculatorConfig.validate() to confirm that invalid configuration
# values trigger ConfigurationError with the expected messages.
# ----------------------------------------------------------------------
def test_invalid_max_history_size():
    with pytest.raises(ConfigurationError, match="max_history_size must be positive"):
        config = CalculatorConfig(max_history_size=-1)
        config.validate()


def test_invalid_precision():
    with pytest.raises(ConfigurationError, match="precision must be positive"):
        config = CalculatorConfig(precision=-1)
        config.validate()


def test_invalid_max_input_value():
    with pytest.raises(ConfigurationError, match="max_input_value must be positive"):
        config = CalculatorConfig(max_input_value=Decimal("-1"))
        config.validate()


# ----------------------------------------------------------------------
# TEST: auto_save environment variable parsing
# ----------------------------------------------------------------------
# Confirms that CalculatorConfig correctly parses `auto_save` environment values
# like 'true', '1', 'false', and '0' into the expected boolean values.
# ----------------------------------------------------------------------
def test_auto_save_env_var_true():
    os.environ['CALCULATOR_AUTO_SAVE'] = 'true'
    config = CalculatorConfig(auto_save=None)
    assert config.auto_save is True


def test_auto_save_env_var_one():
    os.environ['CALCULATOR_AUTO_SAVE'] = '1'
    config = CalculatorConfig(auto_save=None)
    assert config.auto_save is True


def test_auto_save_env_var_false():
    os.environ['CALCULATOR_AUTO_SAVE'] = 'false'
    config = CalculatorConfig(auto_save=None)
    assert config.auto_save is False


def test_auto_save_env_var_zero():
    os.environ['CALCULATOR_AUTO_SAVE'] = '0'
    config = CalculatorConfig(auto_save=None)
    assert config.auto_save is False


# ----------------------------------------------------------------------
# TEST: Environment overrides vs defaults
# ----------------------------------------------------------------------
# - test_environment_overrides: Ensures environment variables override defaults.
# - test_default_fallbacks: Clears environment to verify internal default values.
# ----------------------------------------------------------------------
def test_environment_overrides():
    config = CalculatorConfig()
    assert config.max_history_size == 500
    assert config.auto_save is False
    assert config.precision == 8
    assert config.max_input_value == Decimal("1000")
    assert config.default_encoding == 'utf-16'


def test_default_fallbacks():
    clear_env_vars(
        'CALCULATOR_MAX_HISTORY_SIZE', 'CALCULATOR_AUTO_SAVE', 'CALCULATOR_PRECISION',
        'CALCULATOR_MAX_INPUT_VALUE', 'CALCULATOR_DEFAULT_ENCODING'
    )
    config = CalculatorConfig()
    assert config.max_history_size == 1000
    assert config.auto_save is True
    assert config.precision == 10
    assert config.max_input_value == Decimal("1e999")
    assert config.default_encoding == 'utf-8'


# ----------------------------------------------------------------------
# TEST: Project root helper
# ----------------------------------------------------------------------
# Verifies that get_project_root() correctly resolves the root directory of
# the project, ensuring relative imports and path references work as expected.
# ----------------------------------------------------------------------
def test_get_project_root():
    from app.calculator_config import get_project_root
    assert (get_project_root() / "app").exists()


# ----------------------------------------------------------------------
# TEST: Individual property helpers
# ----------------------------------------------------------------------
# Confirms that each directory/file property resolves correctly relative
# to the specified base_dir when no environment overrides are present.
# ----------------------------------------------------------------------
def test_log_dir_property():
    clear_env_vars('CALCULATOR_LOG_DIR')
    config = CalculatorConfig(base_dir=Path('/new_base_dir'))
    assert config.log_dir == Path('/new_base_dir/logs').resolve()


def test_history_dir_property():
    clear_env_vars('CALCULATOR_HISTORY_DIR')
    config = CalculatorConfig(base_dir=Path('/new_base_dir'))
    assert config.history_dir == Path('/new_base_dir/history').resolve()


def test_log_file_property():
    clear_env_vars('CALCULATOR_LOG_FILE')
    config = CalculatorConfig(base_dir=Path('/new_base_dir'))
    assert config.log_file == Path('/new_base_dir/logs/calculator.log').resolve()


def test_history_file_property():
    clear_env_vars('CALCULATOR_HISTORY_FILE')
    config = CalculatorConfig(base_dir=Path('/new_base_dir'))
    assert config.history_file == Path('/new_base_dir/history/calculator_history.csv').resolve()
