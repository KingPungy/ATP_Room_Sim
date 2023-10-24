import pytest
import sys
sys.path.insert(0,"..\\ATP_Room_Sim") # Add the directory containing the module.py file to the Python path
from PyQt5.QtWidgets import QApplication
from room_simulator import Room
import room_simulator as rs

def test_Room_initialization():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    assert room is not None
    assert isinstance(room, Room)

def test_getTemperature():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    room.setOutsideTemperature(25.0)
    offset = room.getTemperature() - 25.0
    assert room.getTemperature() == 25.0 + offset
    room.setOutsideTemperature(30.0)
    room.setTemperature(25.0)
    assert room.getTemperature() >= 25.0 + offset
    room.setOutsideTemperature(10.0)
    room.setTemperature(25.0)
    assert room.getTemperature() <= 25.0 + offset
    
def test_setTemperature():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    room.setOutsideTemperature(25.0)
    offset = room.getTemperature() - 25.0
    room.setOutsideTemperature(30.0)
    room.setTemperature(30.0)
    assert room.getTemperature() == 30.0 + offset

def test_getHumidity():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    assert room.getHumidity() == 50.0
    room.setHumidity(60.0)
    assert room.getHumidity() == 60.0
    
def test_setHumidity():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    room.setHumidity(60.0)
    assert room.getHumidity() == 60.0
    room.setHumidity(40.0)
    assert room.getHumidity() == 40.0
    
def test_isHeaterActive():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    assert room.isHeaterActive() == False
    room.activateHeater(True)
    assert room.isHeaterActive() == True
    
def test_activateHeater():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    room.activateHeater(True)
    assert room.isHeaterActive() == True
    room.activateHeater(False)
    assert room.isHeaterActive() == False
    
def test_isCoolerActive():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    assert room.isCoolerActive() == False
    room.activateCooler(True)
    assert room.isCoolerActive() == True
    
def test_activateCooler():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    room.activateCooler(True)
    assert room.isCoolerActive() == True
    room.activateCooler(False)
    assert room.isCoolerActive() == False
    
def test_getHeaterPower():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    assert room.getHeaterPower() == 1000.0
    
def test_setHeaterPower():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    assert room.getHeaterPower() == 1000.0
    room.setHeaterPower(2000.0)
    assert room.getHeaterPower() == 2000.0
    
def test_getCoolerPower():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    assert room.getCoolerPower() == 2000.0

def test_setCoolerPower():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    assert room.getCoolerPower() == 2000.0
    room.setCoolerPower(1000.0)
    assert room.getCoolerPower() == 1000.0
    
def test_getOutsideTemperature():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    offset = room.getOutsideTemperature() - 30.0
    assert room.getOutsideTemperature() == 30.0 + offset
    room.setOutsideTemperature(25.0)
    assert room.getOutsideTemperature() == 25.0 + offset
    
def test_setOutsideTemperature():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    room.setOutsideTemperature(35.0)
    offset = room.getOutsideTemperature() - 35.0
    assert room.getOutsideTemperature() == 35.0 + offset
    
def test_calculateTempDelta():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    assert room.calculateTempDelta(1000) == 1.3994168043136597
    
def test_calculateHeatExchange():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    assert room.calculateHeatExchange() == pytest.approx(240,0.1)

def test_set_invalid_dimensions():
    with pytest.raises(ValueError):
        room = Room(25.0, 30.0, 50.0, [10.0, 10.0])

def test_set_invalid_humidity():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    with pytest.raises(ValueError):
        room.setHumidity(200.0)  # Attempt to set an unrealistic humidity

    with pytest.raises(ValueError):
        room.setHumidity(-10.0)  # Attempt to set an unrealistic humidity

def test_set_heater_power_invalid_value():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    with pytest.raises(ValueError):
        room.setHeaterPower(-500.0)

def test_set_cooler_power_invalid_value():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    with pytest.raises(ValueError):
        room.setCoolerPower(-1000.0)


def test_set_out_of_sensor_range_outside_temperature():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])
    offset = room.getOutsideTemperature() - 30.0
    room.setOutsideTemperature(100.0)
    assert room.getOutsideTemperature() == pytest.approx(80.0 + offset,0.1)


def test_get_set_LightLevelLux():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])  
    assert room.getLightLevelLux() == 10000  
    room.setLightLevelLux(500)
    assert room.getLightLevelLux() == 500

    # Test invalid values
    with pytest.raises(ValueError):
        room.setLightLevelLux(-1)
    with pytest.raises(ValueError):
        room.setLightLevelLux(0)
    with pytest.raises(ValueError):
        room.setLightLevelLux(100001)

def test_is_sunscreen_and_activate_sunscreen():
    room = Room(25.0, 30.0, 50.0, [10.0, 10.0, 2.0])  
    assert room.isSunscreenActive() == False
    room.activateSunscreen(True)
    assert room.isSunscreenActive() == True
    room.activateSunscreen(False)
    assert room.isSunscreenActive() == False


if __name__ == "__main__":
    
    print(f"Pybind11 Module Version: {rs.__version__}")
    app = QApplication([]) # needed for SIMgui tests that rely on QApplication instance
    pytest.main(['-v']) # run pytest with verbose output
    sys.exit() # shutdown Qt event loop that was started by QApplication([])
    
