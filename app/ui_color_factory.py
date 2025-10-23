from colorama import Fore, Style, init 

init(autoreset=True) 

class ColorFormatter:
    """Base class for colorized message formatting."""
    def format(self, message: str) -> str:
        raise NotImplementedError("Subclasses must implement format()")

class SuccessFormatter(ColorFormatter):
    """Formatter for success messages."""
    def format(self, message: str) -> str:
        return f"{Fore.GREEN}{Style.BRIGHT}{message}{Style.RESET_ALL}"

class ErrorFormatter(ColorFormatter):
    """Formatter for error messages."""
    def format(self, message: str) -> str:
        return f"{Fore.RED}{Style.BRIGHT}{message}{Style.RESET_ALL}"

class WarningFormatter(ColorFormatter):
    """Formatter for warning messages."""
    def format(self, message: str) -> str:
        return f"{Fore.MAGENTA}{message}{Style.RESET_ALL}"

class InfoFormatter(ColorFormatter):
    """Formatter for informational messages."""
    def format(self, message: str) -> str:
        return f"{Fore.YELLOW}{message}{Style.RESET_ALL}"

class ResultFormatter(ColorFormatter):
    """Formatter for result messages."""
    def format(self, message: str) -> str:
        return f"{Fore.CYAN}{Style.BRIGHT}{message}{Style.RESET_ALL}"

class PromptFormatter(ColorFormatter):
    """Formatter for prompt messages."""
    def format(self, message: str) -> str:
        return f"{Fore.BLUE}{message}{Style.RESET_ALL}"

# Factory class
class ColorFormatterFactory:
    """Factory to create formatter instances by type name."""
    _formatters = {
        "success": SuccessFormatter,
        "error": ErrorFormatter,
        "warning": WarningFormatter,
        "info": InfoFormatter,
        "result": ResultFormatter,
        "prompt": PromptFormatter,
    }

    @classmethod
    def get_formatter(cls, message_type: str) -> ColorFormatter:
        formatter_class = cls._formatters.get(message_type.lower(), InfoFormatter)
        return formatter_class()