########################
# Color Formatting     #
########################

"""
This module provides centralized colorized message formatting for console output
using the `colorama` library. It implements a Singleton design pattern to ensure
consistent styling across the entire application.

Key Features:
1. Singleton Implementation:
   - Ensures only one shared instance of ColorFormatter exists
   - Provides a global access point for message styling
   - Avoids unnecessary memory overhead from multiple instances

2. Standardized Color Schemes:
   - success(message): Bright green
   - error(message): Bright red
   - warning(message): Magenta
   - info(message): Yellow
   - result(message): Bright cyan
   - prompt(message): Blue
   - All methods automatically reset formatting after the message

3. Integration & Consistency:
   - Designed for CLI tools, including the calculator REPL
   - Promotes uniform color usage across all modules
   - Simplifies code maintenance and ensures visual consistency

4. Design Rationale:
   - Singleton chosen because formatting is stateless and deterministic
   - Factory pattern not needed due to fixed, reusable formatting behaviors
   - Provides lightweight, easy-to-use interface for developers
"""

from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class ColorFormatter:
    """
    Singleton class for centralized colorized message formatting.

    This class provides reusable and consistent color formatting for console output
    using the `colorama` library. It follows the Singleton design pattern to ensure that
    only one shared formatter instance exists throughout the application.

    The formatter provides standardized color schemes for different types of messages
    (e.g., success, error, info, warnings, results, prompts). This allows all modules
    and command-line interfaces in the project to maintain a unified visual style.

    --------------------------------------------------------------------------
    Why Singleton?
    --------------------------------------------------------------------------
    The Singleton pattern is used because:
      - Color formatting is **stateless** — all methods produce deterministic,
        side-effect-free results, so multiple instances are unnecessary.
      - A single, globally accessible instance is sufficient for consistent styling
        across the entire application.
      - Reusing the same instance improves efficiency and ensures all messages
        adhere to the same formatting rules.
      - It simplifies integration in CLI tools (like the calculator REPL) by allowing
        universal access to a single shared formatter without dependency injection.

    --------------------------------------------------------------------------
    Why NOT a Factory?
    --------------------------------------------------------------------------
    A Factory pattern is typically used when:
      - You need to **create multiple types of related objects** dynamically.
      - Each object may have unique initialization parameters or internal state.

    In this case:
      - All formatting behaviors are **fixed and stateless** (no runtime configuration).
      - Each style (success, error, info, etc.) is predefined and used directly.
      - Creating multiple formatter instances adds unnecessary complexity and memory overhead.

    Therefore, a Singleton is the most appropriate design choice — it provides a
    single global access point for message styling while keeping the code lightweight,
    consistent, and easy to maintain.

    --------------------------------------------------------------------------
    Example Usage:
    --------------------------------------------------------------------------
        >>> formatter = ColorFormatter()
        >>> print(formatter.success("Operation completed successfully!"))
        >>> print(formatter.error("Invalid input detected."))
        >>> print(formatter.info("Loading configuration..."))
        >>> print(formatter.result("Result: 42"))
        >>> print(formatter.prompt("Enter your choice: "))

    All calls to ColorFormatter() return the same shared instance.
    """

    _instance = None  # Holds the single shared instance

    def __new__(cls):
        """Ensure only one instance of ColorFormatter exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # --- Formatting Methods ---

    def success(self, message: str) -> str:
        """Format success messages in bright green."""
        return f"{Fore.GREEN}{Style.BRIGHT}{message}{Style.RESET_ALL}"

    def error(self, message: str) -> str:
        """Format error messages in bright red."""
        return f"{Fore.RED}{Style.BRIGHT}{message}{Style.RESET_ALL}"

    def warning(self, message: str) -> str:
        """Format warning messages in magenta."""
        return f"{Fore.MAGENTA}{message}{Style.RESET_ALL}"

    def info(self, message: str) -> str:
        """Format informational messages in yellow."""
        return f"{Fore.YELLOW}{message}{Style.RESET_ALL}"

    def result(self, message: str) -> str:
        """Format calculation results in bright cyan."""
        return f"{Fore.CYAN}{Style.BRIGHT}{message}{Style.RESET_ALL}"

    def prompt(self, message: str) -> str:
        """Format user input prompts in blue."""
        return f"{Fore.BLUE}{message}{Style.RESET_ALL}"
