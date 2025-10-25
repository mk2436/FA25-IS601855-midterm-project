########################
# Logging Management   #
########################

"""
This module implements logging of calculator operations using the Observer
design pattern, ensuring calculation events are recorded for auditing and debugging.

Key Features:
1. Observer Integration:
   - LoggingObserver subscribes to calculation events
   - Follows the Observer pattern for decoupled event handling
   - Receives updates whenever a new calculation is performed

2. Automatic Logging:
   - Logs operation type, operands, and result to the configured log file
   - Ensures all calculations are traceable and auditable
   - Raises exceptions if invalid calculation objects are passed

3. Integration & Extensibility:
   - Designed to integrate seamlessly with the Calculator and HistoryObserver system
   - Supports multiple observers simultaneously
   - Facilitates maintainability and future enhancements for custom logging
"""


import logging
from pathlib import Path
import logging
from typing import Optional
from app.calculator_config import CalculatorConfig



def configure_logging(config: Optional[CalculatorConfig] = None) -> None:
    """
    Configure Python logging using settings from CalculatorConfig.

    Ensures the log directory exists and sets up file logging with INFO level.
    """
    if config is None:
        config = CalculatorConfig()

    log_dir = Path(config.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = Path(config.log_file)

    logging.basicConfig(
        filename=str(log_file),
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        force=True
    )
    logging.info(f"Logging initialized at: {log_file}")