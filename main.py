# python --version: 3.10.9
from functools import wraps
import time
import inspect
from PyQt5 import QtCore #, QtWidgets  # for gui widgets
from PyQt5.QtWidgets import QApplication #, QMainWindow, QWidget  # for gui window and app

import sys  # for system operations
import reactivex as rx

# from room import Room  # Old room.py class and temperature generator
from room_simulator import Room # New room class and temperature generator
import room_simulator as rs # includes mockArduino and Room classes
from SIMgui import SIMgui # gui class with controller
from MockFirmata import MockFirmata # mock arduino class

from constants import * # pin definitions

@staticmethod
def verbose_output_logger_decorator(verbose_enabled, log_output):
    """Decorator for logging verbose output and result of a function
    Args:
        verbose_enabled (bool): Boolean value to enable/disable verbose output
        log_output (bool): Boolean value to enable/disable logging of output
    Returns:
        wrapper (function): Wrapper function with the decorator applied
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if verbose_enabled:
                print(f"Executing function: {func.__name__}")

            result = func(*args, **kwargs)
            if log_output and result is not None:
                print(f"Output of function {func.__name__}: {result}")

            return result
        return wrapper
    return decorator

@staticmethod
def log_time_enabled_decorator(log_time_enabled):
    """Decorator for logging the execution time of a function
    Args:
        log_time_enabled (bool): Boolean value to enable/disable logging of execution time
    Returns:
        wrapper (function): Wrapper function with the decorator applied
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if log_time_enabled:
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                execution_time = end_time - start_time
                print(f"Function {func.__name__} executed in {execution_time} seconds")
                return result
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator

def main() -> None:
    # main pyqt gui setup
    print("Starting program")
    print(f"=====================\nLibrary Versions:\nPython Verion:\t\t{sys.version}\nPyQt5 Verion:\t\t{QtCore.PYQT_VERSION_STR}\nReactivex Verion:\t{rx.__version__}\nRoom_Simulator Version:\t{rs.__version__}\n=====================")

    app = QApplication(sys.argv)

    # pybind11 C++ module room_simulator class
    SIMroom = Room(temperature=25.0, outside_temperature=30,
                   humidity=20.0, room_dimensions=[10, 10, 2]) 
                                # breedte, lengte, hoogte

    mockFirmata = MockFirmata(Port=3, Room=SIMroom)
    if mockFirmata.begin():

        print("MockFirmata connection established")
        pinConnections = [
                f"d:{DHT22_1}:DHT22_1", 
                f"d:{DHT22_2}:DHT22_2",
                f"d:{RELAY_HEATER}:RELAY_HEATER",
                f"d:{RELAY_COOLER}:RELAY_COOLER",
                f"d:{RELAY_SUNSCREEN}:RELAY_SUNSCREEN",
                f"a:{LDR}:LDR"
                ]

        for pin in pinConnections:
            mockFirmata.setPinMode(pin)
        print(f"Pin modes set:\n{pinConnections}\nTo Change pins alter Constants in constants.py\n=====================")


        window = SIMgui(MockFirmata=mockFirmata, graphLength=100)
        
        window.show()

        sys.exit(app.exec_())
    


if __name__ == '__main__':
    
    # Check if the verbose, log-output and log-time flags are provided as command-line arguments
    verbose_enabled = "--verbose" in sys.argv
    log_time_enabled = "--log-time" in sys.argv
    output_logging_enabled = "--log-output" in sys.argv
    print(f"Verbose mode: {verbose_enabled}")
    print(f"Log time mode: {log_time_enabled}")
    print(f"Output logging mode: {output_logging_enabled}")

    # TODO: Add a decorator to the mockFirmata and MockArduino classes

    # Apply the decorators based on the command-line arguments
    if verbose_enabled | log_time_enabled | output_logging_enabled:
        print("Applying decorators")
        # Wrap functions within the SIMgui class
        for name, func in inspect.getmembers(SIMgui, inspect.isfunction):
            setattr(SIMgui, name, verbose_output_logger_decorator(verbose_enabled, output_logging_enabled)(log_time_enabled_decorator(log_time_enabled)(func)))

        # Wrap functions within the MockFirmata class
        for name, func in inspect.getmembers(MockFirmata, inspect.isfunction):
            setattr(MockFirmata, name, verbose_output_logger_decorator(verbose_enabled, output_logging_enabled)(log_time_enabled_decorator(log_time_enabled)(func)))
        
        # Create wrapper functions and apply decorators for the Room class functions
        for attr_name, attr_value in inspect.getmembers(rs.Room):
            if callable(attr_value) and not inspect.isclass(attr_value) and attr_name != "__getattribute__":
                wrapper_func = verbose_output_logger_decorator(verbose_enabled, output_logging_enabled)(log_time_enabled_decorator(log_time_enabled)(attr_value))
                setattr(rs.Room, attr_name, wrapper_func)

        # Create wrapper functions and apply decorators for the MockArduino class functions
        for attr_name, attr_value in inspect.getmembers(rs.mockArduino):
            if callable(attr_value) and not inspect.isclass(attr_value) and attr_name != "__getattribute__":
                wrapper_func = verbose_output_logger_decorator(verbose_enabled, output_logging_enabled)(log_time_enabled_decorator(log_time_enabled)(attr_value))
                setattr(rs.mockArduino, attr_name, wrapper_func)
        
    # setup the main program
    main()

    pass
