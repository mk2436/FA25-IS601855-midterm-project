# Enhanced Calculator Command-Line Application

## Project Description
This project implements a sophisticated command-line calculator that showcases modern software engineering principles, design patterns, and best practices. It's built with a focus on maintainability, extensibility, and robust error handling.

### Core Capabilities:
1. **Mathematical Operations**
   - Basic: Addition, Subtraction, Multiplication, Division
   - Advanced: Power, Root, Modulus, Integer Division
   - Special: Percentage Calculations, Absolute Differences
   - Input Validation: Comprehensive error checking with detailed feedback
   - Precision: Uses Python's Decimal type for accurate calculations

2. **State Management**
   - History Tracking: Records all calculations with timestamps
   - Undo/Redo: Supports multiple levels of operation reversal
   - Session Persistence: Auto-saves history to prevent data loss
   - Batch Operations: Queue multiple calculations for sequential execution

3. **User Interface**
   - Interactive REPL: Command-line interface with intuitive prompts
   - Color-Coded Output: Visual distinction between different types of messages
   - Dynamic Help System: Auto-updating command documentation
   - Error Handling: Clear, user-friendly error messages
   - Operation Cancellation: Abort operations safely at any point

4. **Configuration System**
   - Environment Variables: Flexible runtime configuration via `.env` file
   - Customizable Settings: History size, precision, auto-save behavior
   - Directory Management: Organized logs and history storage
   - Default Fallbacks: Sensible defaults for all settings

5. **Development Features**
   - Comprehensive Testing: Unit tests with pytest
   - Code Coverage: Enforces high test coverage standards
   - Type Safety: Strong typing and validation throughout
   - CI/CD Integration: Automated testing via GitHub Actions
   - Modular Design: Clear separation of concerns
   - Documentation: Detailed docstrings and comments

### Design Patterns used:

1. **Factory Pattern** (`OperationFactory` in `operations.py`):
   - Creates different operation objects (Add, Subtract, Multiply, etc.)
   - Centralizes object creation logic
   - Supports dynamic registration of new operations
   - Used by Calculator to instantiate operation strategies

2. **Memento Pattern** (`CalculatorMemento` in `calculator_memento.py`):
   - Implements undo/redo functionality
   - Captures and restores calculator state snapshots
   - Maintains history with timestamps
   - Stores complete calculation sequences
   - Supports serialization for state persistence

3. **Observer Pattern** (`LoggingObserver` and `AutoSaveObserver` in `history.py`):
   - Notifies observers when new calculations are performed
   - `LoggingObserver`: Logs all calculations and events
   - `AutoSaveObserver`: Automatically saves history to file
   - Easily extensible for adding new observers

4. **Decorator Pattern** (`HelpDecorator` in `help_menu.py`):
   - Dynamically builds help menu content
   - `BasicHelp`: Core help text component
   - `OperationsHelpDecorator`: Adds available operations to help
   - Supports layered decoration for future enhancements

5. **Command Pattern** (`Command`, `OperationCommand`, `CommandQueue` in `commands.py`):
   - Encapsulates operations as command objects
   - Supports operation queueing and batch execution
   - `CommandQueue`: Manages sequence of operations
   - Facilitates undo/redo implementation
   - Decouples operation execution from Calculator

6. **Singleton Pattern** (`ColorFormatter` in `ui_color.py`):
   - Ensures single instance for color formatting
   - Provides consistent color scheme across application
   - Manages terminal output styling
   - Efficient resource usage for formatting operations

7. **Strategy Pattern** (implemented in `Calculator` class):
   - Dynamic operation strategy switching
   - Allows changing calculation behavior at runtime
   - Used with Factory Pattern for operation creation
   - Supports flexible operation execution

Each pattern serves a specific purpose in making the calculator modular, maintainable, and extensible while following SOLID principles.

---


## Directory Structure

```
project_root/
├── app/
│   ├── __init__.py
│   ├── calculator.py
│   ├── calculation.py
│   ├── calculator_config.py
│   ├── calculator_memento.py
│   ├── exceptions.py
│   ├── history.py
│   ├── input_validators.py
│   ├── operations.py
│   └── logger.py
├── tests/
│   ├── __init__.py
│   ├── test_calculator.py
│   ├── test_calculation.py
│   ├── test_operations.py
│   └── ...
├── .env
├── requirements.txt
├── README.md
└── .github/
    └── workflows/
        └── python-app.yml
```

---

## Installation Instructions

1. **Clone the repository:**
```bash
git clone https://github.com/mk2436/FA25-IS601855-midterm-project.git
cd FA25-IS601855-midterm-project
```

2. **Create and activate a virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

---

## Configuration Setup

1. **Create a `.env` file in the project root.**
2. **Example `.env` file:**
```dotenv
CALCULATOR_LOG_DIR=./logs
CALCULATOR_HISTORY_DIR=./history
CALCULATOR_MAX_HISTORY_SIZE=1000
CALCULATOR_AUTO_SAVE=true
CALCULATOR_PRECISION=4
CALCULATOR_MAX_INPUT_VALUE=1000000
CALCULATOR_DEFAULT_ENCODING=utf-8
```

3. **The application will load and validate these settings on startup. Default values are used if variables are missing.**

### Supported environment variables

| Variable | Default | Description |
|---|---|---|
| CALCULATOR_BASE_DIR | project root | Base directory for logs/history (resolved to project root by default) |
| CALCULATOR_MAX_HISTORY_SIZE | 1000 | Maximum number of history entries to retain |
| CALCULATOR_AUTO_SAVE | true | Auto-save history after each calculation (true/false or 1/0) |
| CALCULATOR_PRECISION | 10 | Number of decimal places used for calculations |
| CALCULATOR_MAX_INPUT_VALUE | 1e999 | Maximum numeric value accepted as input |
| CALCULATOR_DEFAULT_ENCODING | utf-8 | Default file encoding used for reading/writing files |
| CALCULATOR_LOG_DIR | <base_dir>/logs | Directory where log files are stored (overrides default logs path) |
| CALCULATOR_HISTORY_DIR | <base_dir>/history | Directory where history files are stored (overrides default history path) |
| CALCULATOR_HISTORY_FILE | <history_dir>/calculator_history.csv | File path used when saving/loading history (CSV) |
| CALCULATOR_LOG_FILE | <log_dir>/calculator.log | File path used for application logs |


---

## Usage Guide

1. **Start the Calculator:**
```bash
python main.py
```

**Available commands and usage instructions.**

### Operations

| Command | Description |
|---|---|
| add | Add two numbers |
| subtract | Subtract second number from first |
| multiply | Multiply two numbers |
| divide | Divide first number by second (error on zero) |
| power | Raise base to exponent (no negative exponents) |
| root | Calculate the nth root of a number |
| modulus | Compute remainder of division |
| int_divide | Integer division (floor/truncate quotient) |
| percentage | Calculate (a * b) / 100 (percentage of a) |
| abs_diff | Absolute difference between two numbers |

### Queuing Operations

| Command | Description |
|---|---|
| queue add | Add an operation to the queue |
| queue run | Execute all queued operations |
| queue show | Show all queued operations |
| queue clear | Clear the operation queue |

### Other Commands

| Command | Description |
|---|---|
| history | Show calculation history |
| clear | Clear calculation history |
| undo | Undo the last calculation |
| redo | Redo the last undone calculation |
| save | Save calculation history to file |
| load | Load calculation history from file |
| exit | Exit the calculator |


3. **Performing Calculations:**
- Enter the operation command (e.g., `add`) and follow the prompts for numbers.
- You can type `'cancel'` at any number prompt to abort the operation.

**Example:**
```
Enter command: add

Enter numbers (or 'cancel' to abort):
First number: 3
Second number: 2

Result: 5
```

4. **History Management:**
- `history` – Show all previous calculations.
- `clear` – Clear calculation history.
- `undo` – Undo the last calculation.
- `redo` – Redo the last undone calculation.

5. **Queueing Operations:**
- `queue add` – Add an operation to the queue.
- `queue show` – Display all queued operations.
- `queue run` – Execute all queued operations.
- `queue clear` – Clear all queued operations.

6. **Saving and Loading History:**
- `save` – Save the current history to CSV file.
- `load` – Load history from CSV file.

7. **Exiting the Calculator:**
- `exit` – Exit the application.
- Any unsaved history will be saved automatically before exit.

8. **Notes:**
- All operations validate input and handle errors gracefully.
- The REPL interface guides the user through each command with prompts.
- Optional features like queueing and color-coded outputs enhance usability.

---
## Queue Operations Usage

The calculator supports queuing of operations to execute them in batch. This is useful for performing multiple calculations sequentially without entering each command individually.

### Queue Commands:

- `queue add` – Add an operation to the queue.
- `queue show` – Display all operations currently in the queue.
- `queue run` – Execute all queued operations in order.
- `queue clear` – Clear all operations from the queue.

### Example Workflow:

1. **View queue commands:**
```
Enter command: queue
Queue commands: add, run, show, clear
```

2. **Add operation to queue:**
```
Enter command: queue add
Operation name: divide
First number: 2
Second number: 3
Operation queued
```

3. **Show queued operations:**
```
Enter command: queue show
1. Division(2, 3)
```

4. **Execute all queued operations:**
```
Enter command: queue run
1. 0.6666666666666666666666666667
```

### Notes:
- Queued operations maintain their input values and operation type.
- You can mix immediate calculations with queued operations.
- The queue can be cleared at any time using `queue clear`.

---

## History Management Usage

The calculator provides comprehensive history management capabilities, allowing you to track, review, modify, and persist your calculation history. This feature is built using the Memento pattern for state management and Observer pattern for auto-saving.

### History Commands:

- `history` – Display all previous calculations with results
- `clear` – Remove all calculations from history
- `undo` – Revert the last calculation (multiple undos supported)
- `redo` – Restore previously undone calculations
- `save` – Write history to CSV file for persistence
- `load` – Restore history from previously saved CSV file

### Example Workflow:

1. **Perform some calculations:**
```
Enter command: add
First number: 5
Second number: 3
Result: 8

Enter command: multiply
First number: 4
Second number: 2
Result: 8
```

2. **View calculation history:**
```
Enter command: history
1. Addition(5, 3) = 8
2. Multiplication(4, 2) = 8
```

3. **Undo last calculation:**
```
Enter command: undo
Last calculation undone

Enter command: history
1. Addition(5, 3) = 8
```

4. **Redo the undone calculation:**
```
Enter command: redo
Calculation restored

Enter command: history
1. Addition(5, 3) = 8
2. Multiplication(4, 2) = 8
```

5. **Save history to file:**
```
Enter command: save
History saved successfully to ./history/calculator_history.csv
```

The history is saved in CSV format for easy analysis and importing into spreadsheets:
```csv
operation,operand1,operand2,result,timestamp
Addition,5,3,8,2025-10-24T21:00:51.244757
Multiplication,4,2,8,2025-10-24T21:30:44.582537
```

### Notes:
- History is automatically saved after each calculation if `CALCULATOR_AUTO_SAVE` is enabled
- Maximum history size is configurable via `CALCULATOR_MAX_HISTORY_SIZE`
- History includes timestamps and full calculation details
- Undo/redo operations maintain the complete calculation state
- History can be exported to CSV for analysis or backup

---

## Testing Instructions

1. **Run unit tests with pytest:**
```bash
pytest
```

2. **Check test coverage:**
```bash
pytest --cov=app --cov-fail-under=90
```

## CI/CD Information

- GitHub Actions workflow is configured in `.github/workflows/python-app.yml`.
- Automatically runs tests and measures coverage on pushes or pull requests to the main branch.
- Enforces 100% test coverage threshold.

---

## Logging

- Logging is handled by the `Logger` class.
- All calculations, errors, and important events are logged to the file specified by `CALCULATOR_LOG_DIR`.
- Supports `INFO`, `WARNING`, and `ERROR` levels.

Sample log entries (stored in the file defined by `CALCULATOR_LOG_FILE`):

```text
2025-10-24 21:00:41,123 - INFO - Calculator initialized with configuration
2025-10-24 21:00:41,124 - INFO - Added observer: LoggingObserver
2025-10-24 21:00:41,124 - INFO - Added observer: AutoSaveObserver
2025-10-24 21:00:51,243 - INFO - Set operation: Addition
2025-10-24 21:00:51,244 - INFO - Calculation performed: Addition (3, 2) = 5
2025-10-24 21:00:51,327 - INFO - History saved successfully to /history/calculator_history.csv
2025-10-24 21:00:51,327 - INFO - History auto-saved

```

---