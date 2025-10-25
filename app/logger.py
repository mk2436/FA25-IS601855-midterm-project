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
from app.calculation import Calculation
from app.history import HistoryObserver


class LoggingObserver(HistoryObserver):
    """
    Observer that logs calculations to a file.

    Implements the Observer pattern by listening for new calculations and logging
    their details to a log file.
    """

    def update(self, calculation: Calculation) -> None:
        """
        Log calculation details.

        This method is called whenever a new calculation is performed. It records
        the operation, operands, and result in the log file.

        Args:
            calculation (Calculation): The calculation that was performed.
        """
        if calculation is None:
            raise AttributeError("Calculation cannot be None")
        logging.info(
            f"Calculation performed: {calculation.operation} "
            f"({calculation.operand1}, {calculation.operand2}) = "
            f"{calculation.result}"
        )