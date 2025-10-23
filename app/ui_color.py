from colorama import Fore, Style, init

init(autoreset=True)


class ColorFormatter:
    """
    Singleton class for centralized colorized message formatting.

    This class provides reusable and consistent color formatting for console output 
    using the `colorama` library. It follows the Singleton design pattern to ensure that 
    only one shared formatter instance exists throughout the application.

    === Why Singleton? ===
    The Singleton pattern is used here because:
        - Formatting logic is stateless and does not depend on unique data per instance.
        - A single, globally accessible instance is sufficient for applying color styles 
        consistently across all parts of the application (e.g., CLI prompts, logs, errors).
        - It prevents unnecessary object creation overhead by reusing the same instance 
        instead of instantiating new formatters for every print operation.
        - It simplifies integration — any module can access the same shared formatter 
        without dependency injection or object lifecycle management.

    === Why NOT a Factory? ===
    A Factory pattern is generally used when you need to dynamically create different 
    kinds of objects (often with varying configurations or states). In this case, 
    color formatting methods (success, error, info, etc.) are:
        - Fixed in behavior (always apply the same style).
        - Stateless (no unique runtime data).
        - Accessed frequently but uniformly across the app.

    Therefore, a Factory would add unnecessary complexity — creating new formatter 
    objects that all behave identically. The Singleton approach offers a simpler, 
    more efficient solution that aligns with the "one global styling utility" intent.


    All calls to ColorFormatter() will return the same shared instance.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # --- Formatting Methods ---
    def success(self, message: str) -> str:
        """Format a success message in green and bright style."""
        return f"{Fore.GREEN}{Style.BRIGHT}{message}{Style.RESET_ALL}"

    def error(self, message: str) -> str:
        """Format an error message in red and bright style."""
        return f"{Fore.RED}{Style.BRIGHT}{message}{Style.RESET_ALL}"

    def warning(self, message: str) -> str:
        """Format a warning message in magenta."""
        return f"{Fore.MAGENTA}{message}{Style.RESET_ALL}"

    def info(self, message: str) -> str:
        """Format an informational message in yellow."""
        return f"{Fore.YELLOW}{message}{Style.RESET_ALL}"

    def result(self, message: str) -> str:
        """Format a result message in cyan and bright style."""
        return f"{Fore.CYAN}{Style.BRIGHT}{message}{Style.RESET_ALL}"

    def prompt(self, message: str) -> str:
        """Format a prompt message in blue."""
        return f"{Fore.BLUE}{message}{Style.RESET_ALL}"

    def dim(self, message: str) -> str:
        """Format a dimmed message in light black."""
        return f"{Style.DIM}{Fore.LIGHTBLACK_EX}{message}{Style.RESET_ALL}"
