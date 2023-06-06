import pytest
import sys
sys.path.insert(0,"..\\ATP_CppRoomSim_PyGUI") # Add the directory containing the module.py file to the Python path
from PyQt5.QtWidgets import QApplication
from room_simulator import Room
import room_simulator as rs

def test_getTemperature():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    room.setOutsideTemperature(25.0)
    assert room.getTemperature() == 25.0
    room.setOutsideTemperature(30.0)
    room.setTemperature(25.0)
    assert room.getTemperature() >= 25.0
    room.setOutsideTemperature(10.0)
    room.setTemperature(25.0)
    assert room.getTemperature() <= 25.0
    
def test_setTemperature():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    room.setTemperature(30.0)
    assert room.getTemperature() == 30.0

def test_getHumidity():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    assert room.getHumidity() == 50.0
    
def test_setHumidity():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    room.setHumidity(60.0)
    assert room.getHumidity() == 60.0
    
def test_isHeaterActive():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    assert room.isHeaterActive() == False
    
def test_activateHeater():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    room.activateHeater(True)
    assert room.isHeaterActive() == True
    
def test_isCoolerActive():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    assert room.isCoolerActive() == False
    
def test_activateCooler():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    room.activateCooler(True)
    assert room.isCoolerActive() == True
    
def test_getHeaterPower():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    assert room.getHeaterPower() == 1000.0
    
def test_setHeaterPower():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    room.setHeaterPower(1000.0)
    assert room.getHeaterPower() == 1000.0
    
def test_getCoolerPower():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    assert room.getCoolerPower() == 2000.0
    
def test_setCoolerPower():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    room.setCoolerPower(1000.0)
    assert room.getCoolerPower() == 1000.0
    
def test_getOutsideTemperature():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    assert room.getOutsideTemperature() == 30.0
    
def test_setOutsideTemperature():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    room.setOutsideTemperature(35.0)
    assert room.getOutsideTemperature() == 35.0
    
def test_calculateTempDelta():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    assert room.calculateTempDelta(1000) == 1.3994168043136597
    
def test_calculateHeatExchange():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    assert room.calculateHeatExchange() == 239.99998474121094

if __name__ == "__main__":
    
    print(f"Pybind11 Module Version: {rs.__version__}")
    app = QApplication([]) # needed for SIMgui tests that rely on QApplication instance
    pytest.main(['-v']) # run pytest with verbose output
    sys.exit() # shutdown Qt event loop that was started by QApplication([])