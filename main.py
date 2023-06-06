

from PyQt5 import QtCore #, QtWidgets  # for gui widgets
from PyQt5.QtWidgets import QApplication #, QMainWindow, QWidget  # for gui window and app

import sys  # for system operations
import reactivex as rx

# from room import Room  # Old room.py class and temperature generator
from room_simulator import Room # New room class and temperature generator
import room_simulator as rs
from SIMgui import SIMgui


def main() -> None:

    print("Starting program")
    print(f"=====================\nLibrary Versions:\nPython Verion:    {sys.version}\nPyQt5 Verion:     {QtCore.PYQT_VERSION_STR}\nReactivex Verion: {rx.__version__}\nRoom_Simulator Version: {rs.__version__}\n=====================")

    app = QApplication(sys.argv)

    # pybind11 C++ module room_simulator class
    SIMroom = Room(temperature=20.0, outside_temperature=30,
                   humidity=20.0, room_dimensions=[10, 10, 2])
    # make higher order function to pass in the room object

    
    window = SIMgui(SIMroom=SIMroom, graphLength=100)
       
    window.show()

    sys.exit(app.exec_())
    # window()


if __name__ == '__main__':
    # main pyqt gui setup
    main()

    pass
