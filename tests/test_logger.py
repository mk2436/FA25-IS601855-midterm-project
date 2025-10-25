"""
tests/test_logger.py

Unit tests for the configure_logging() function in the logger module.

These tests cover:
- Log directory and file creation under a specified or environment-based base directory.
- Ensuring logging only writes ERROR-level and above messages to the file.
- Proper teardown of logging handlers to avoid cross-test contamination.
"""

import logging
from pathlib import Path

import pytest

from app.logger import configure_logging
from app.calculator_config import CalculatorConfig


def _teardown_logging():
    # Close and remove handlers to avoid interfering with other tests
    for h in list(logging.root.handlers):
        try:
            h.flush()
            h.close()
        except Exception:
            pass
    logging.root.handlers.clear()


def test_configure_creates_log_directory_and_file(tmp_path: Path):
    config = CalculatorConfig(base_dir=tmp_path)

    # Ensure no logs directory exists before
    log_dir = config.log_dir
    if log_dir.exists():
        # clean up to ensure test isolation
        for p in log_dir.rglob('*'):
            p.unlink()
        log_dir.rmdir()

    configure_logging(config)

    try:
        assert log_dir.exists() and log_dir.is_dir()
        # The configured log file's parent directory should exist
        assert config.log_file.parent.exists()
    finally:
        _teardown_logging()


def test_configure_writes_only_error_and_above_to_file(tmp_path: Path):
    config = CalculatorConfig(base_dir=tmp_path)
    configure_logging(config)

    try:
        # Emit an INFO and an ERROR message. configure_logging sets level to ERROR
        logging.info("this is an info message that should not be logged")
        logging.error("this is an error message that should be logged")

        # Ensure handlers flush their output
        for h in logging.root.handlers:
            h.flush()

        # Read the log file and assert only the error message is present
        log_path = config.log_file
        assert log_path.exists(), f"Expected log file at {log_path}"
        content = log_path.read_text(encoding=config.default_encoding)

        assert "this is an error message that should be logged" in content
        assert "this is an info message that should not be logged" not in content
    finally:
        _teardown_logging()


def test_configure_without_argument_respects_environment_base_dir(tmp_path: Path, monkeypatch):
    # Ensure configure_logging() when called without a config reads CALCULATOR_BASE_DIR
    monkeypatch.setenv('CALCULATOR_BASE_DIR', str(tmp_path))

    configure_logging()  # should pick up env var and create logs under tmp_path
    try:
        cfg = CalculatorConfig()
        assert cfg.base_dir == tmp_path.resolve()
        assert cfg.log_dir.exists()
        assert cfg.log_file.parent.exists()
    finally:
        _teardown_logging()
