########################
# History Management   #
########################

"""
This module implements history tracking and observer management for the
calculator application, providing automated reactions to new calculations.

Key Features:
1. Observer Base Class:
   - HistoryObserver defines the interface for calculator observers
   - Requires an update(calculation) method to handle new calculation events
   - Supports modular extensions for custom observer behaviors

2. Auto-Save Functionality:
   - AutoSaveObserver listens for new calculations and triggers auto-saving
   - Automatically saves history if auto-save is enabled in CalculatorConfig
   - Ensures persistence of calculation history without manual intervention
   - Logs auto-save events for transparency and debugging

3. Error Handling & Validation:
   - Validates that calculator instance has required attributes (config, save_history)
   - Raises meaningful exceptions if constraints are not met
   - Ensures calculation objects passed to update() are valid

4. Integration & Extensibility:
   - Designed to integrate seamlessly with the Calculator class
   - Supports multiple observer types for advanced features
   - Follows the Observer design pattern for maintainability and scalability
"""


from abc import ABC, abstractmethod
import logging
from typing import Any
from app.calculation import Calculation


class HistoryObserver(ABC):
    """
    Abstract base class for calculator observers.

    This class defines the interface for observers that monitor and react to
    new calculation events. Implementing classes must provide an update method
    to handle the received Calculation instance.
    """

    @abstractmethod
    def update(self, calculation: Calculation) -> None:
        """
        Handle new calculation event.

        Args:
            calculation (Calculation): The calculation that was performed.
        """
        pass  # pragma: no cover


class AutoSaveObserver(HistoryObserver):
    """
    Observer that automatically saves calculations.

    Implements the Observer pattern by listening for new calculations and
    triggering an automatic save of the calculation history if the auto-save
    feature is enabled in the configuration.
    """

    def __init__(self, calculator: Any):
        """
        Initialize the AutoSaveObserver.

        Args:
            calculator (Any): The calculator instance to interact with.
                Must have 'config' and 'save_history' attributes.

        Raises:
            TypeError: If the calculator does not have the required attributes.
        """
        if not hasattr(calculator, 'config') or not hasattr(calculator, 'save_history'):
            raise TypeError("Calculator must have 'config' and 'save_history' attributes")
        self.calculator = calculator

    def update(self, calculation: Calculation) -> None:
        """
        Trigger auto-save.

        This method is called whenever a new calculation is performed. If the
        auto-save feature is enabled, it saves the current calculation history.

        Args:
            calculation (Calculation): The calculation that was performed.
        """
        if calculation is None:
            raise AttributeError("Calculation cannot be None")
        if self.calculator.config.auto_save:
            self.calculator.save_history()
            logging.info("History auto-saved")
