########################
# Input Validation     #
########################

"""
This module implements input validation and sanitization for the calculator
application, ensuring all numeric inputs conform to configuration rules.

Key Features:
1. Validation Logic:
   - InputValidator.validate_number converts inputs to Decimal
   - Strips strings and normalizes numeric values
   - Enforces maximum allowed value from CalculatorConfig
   - Raises ValidationError for invalid or out-of-range inputs

2. Type Safety & Error Handling:
   - Supports int, float, Decimal, and string inputs
   - Catches decimal conversion errors (InvalidOperation)
   - Provides clear, descriptive error messages for users

3. Integration & Extensibility:
   - Designed to be used by Calculator before performing operations
   - Supports seamless integration with other modules (Calculator, Operations)
   - Centralized validation for maintainability and consistency
"""


from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any
from app.calculator_config import CalculatorConfig
from app.exceptions import ValidationError

@dataclass
class InputValidator:
    """Validates and sanitizes calculator inputs."""
    
    @staticmethod
    def validate_number(value: Any, config: CalculatorConfig) -> Decimal:
        """
        Validate and convert input to Decimal.
        
        Args:
            value: Input value to validate
            config: Calculator configuration
            
        Returns:
            Decimal: Validated and converted number
            
        Raises:
            ValidationError: If input is invalid
        """
        try:
            if isinstance(value, str):
                value = value.strip()
            number = Decimal(str(value))
            if abs(number) > config.max_input_value:
                raise ValidationError(f"Value exceeds maximum allowed: {config.max_input_value}")
            return number.normalize()
        except InvalidOperation as e:
            raise ValidationError(f"Invalid number format: {value}") from e
