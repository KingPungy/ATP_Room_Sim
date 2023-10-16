import pytest
import sys
sys.path.insert(0,"..\\ATP_Room_Sim") # Add the directory containing the module.py file to the Python path
from PyQt5.QtWidgets import QApplication
from room_simulator import Room
import room_simulator as rs
from MockFirmata import MockFirmata

from constants import * # pin definitions


@pytest.fixture
def Firmata():
    SIMroom = Room(temperature=25.0, outside_temperature=30,
                   humidity=20.0, room_dimensions=[10, 10, 2]) 
                                # breedte, lengte, hoogte

    Firmata = MockFirmata(Port=3, Room=SIMroom)
    yield Firmata
    
    
@pytest.fixture
def Firmata_with_pinModes():
    SIMroom = Room(temperature=25.0, outside_temperature=30,
                   humidity=20.0, room_dimensions=[10, 10, 2]) 
                                # breedte, lengte, hoogte

    Firmata = MockFirmata(Port=3, Room=SIMroom)
    Firmata.begin()
    pinConnections = [
                f"d:{DHT22_1}:DHT22_1", 
                f"d:{DHT22_2}:DHT22_2",
                f"d:{RELAY_HEATER}:RELAY_HEATER",
                f"d:{RELAY_COOLER}:RELAY_COOLER",
                f"d:{RELAY_SUNSCREEN}:RELAY_SUNSCREEN",
                f"a:{LDR}:LDR",
                ]

    for pin in pinConnections:
        Firmata.setPinMode(pin)
        
    yield Firmata


def test_MockFirmata_initialization(Firmata):
    assert Firmata is not None
    assert isinstance(Firmata, MockFirmata)

# Test the getRoomObject method
def test_get_room_object(Firmata):
    room = Firmata.getRoomObject()
    assert room is not None  # Assuming it should return a Room object

# Test the setPinMode method
def test_set_pin_mode(Firmata):
    pinConnections = [
                f"d:{DHT22_1}:DHT22_1", 
                f"d:{DHT22_2}:DHT22_2",
                f"d:{RELAY_HEATER}:RELAY_HEATER",
                f"d:{RELAY_COOLER}:RELAY_COOLER",
                f"d:{RELAY_SUNSCREEN}:RELAY_SUNSCREEN",
                f"a:{LDR}:LDR",
                ]

    for pin in pinConnections:
        Firmata.setPinMode(pin)

    # Test the getPinData method
    assert Firmata.digitalRead(DHT22_1) != 0
    assert Firmata.digitalRead(DHT22_2) != 0
    assert Firmata.digitalRead(RELAY_HEATER) == False
    assert Firmata.digitalRead(RELAY_COOLER) == False
    assert Firmata.digitalRead(RELAY_SUNSCREEN) == False
    assert Firmata.analogRead(LDR) != 0

def test_set_pin_mode_invalid_input(Firmata):  
    with pytest.raises(Exception,match="pinMode not in correct format"):
        Firmata.setPinMode("d:7:INVALID_PINMODE")
    
    with pytest.raises(Exception,match="pinDef not in correct format"):
        Firmata.setPinMode("d:7:DHT22_1:extrapart")
    
    with pytest.raises(Exception,match="pinType not in correct format"):
        Firmata.setPinMode("s:7:DHT22_1")
    
    with pytest.raises(Exception,match="Invalid pin number."):
        Firmata.setPinMode("d:-1:DHT22_1")
    
    with pytest.raises(Exception,match="Invalid pin number."):
        Firmata.setPinMode("d:60:DHT22_1")
    
    with pytest.raises(Exception):
        Firmata.setPinMode("d:7:INVALID_PINMODE")
    
    with pytest.raises(Exception):
        Firmata.setPinMode("d:7:INVALID_PINMODE")
    
    with pytest.raises(Exception):
        Firmata.setPinMode("d:7:INVALID_PINMODE")
    

# Test the digitalWrite method
def test_digital_write(Firmata):
    pin = 7
    value = True
    Firmata.digitalWrite(pin, value)
    assert Firmata.digitalRead(pin) == value
    # You can add assertions to check if the digital pin is set correctly

# Test the digitalRead method
def test_digital_analog_read_types(Firmata_with_pinModes):
    # Test the digitalRead method
    assert type(Firmata_with_pinModes.digitalRead(0)) == bool
    assert Firmata_with_pinModes.digitalRead(1) == False
    assert type(Firmata_with_pinModes.digitalRead(DHT22_1)) == type([float,float])
    assert type(Firmata_with_pinModes.digitalRead(DHT22_2)) == type([float,float])
    assert type(Firmata_with_pinModes.digitalRead(RELAY_HEATER)) == bool
    assert type(Firmata_with_pinModes.digitalRead(RELAY_COOLER)) == bool
    assert type(Firmata_with_pinModes.digitalRead(RELAY_SUNSCREEN)) == bool
    # Test the analogRead method
    assert type(Firmata_with_pinModes.analogRead(LDR)) == int
    
    with pytest.raises(ValueError):
        Firmata_with_pinModes.analogRead(1) # analaog pin 1 is not set as LDR
        
    with pytest.raises(ValueError):
        Firmata_with_pinModes.digitalRead(-1)
    
    with pytest.raises(ValueError):
        Firmata_with_pinModes.digitalRead(100)
        
    with pytest.raises(ValueError):
        Firmata_with_pinModes.analogRead(-1)
    
    with pytest.raises(ValueError):
        Firmata_with_pinModes.analogRead(17)
        
    

# Test the analogRead method
def test_analog_read(Firmata):
    pin = 0
    Firmata.setPinMode(f"a:{pin}:LDR")
    result = Firmata.analogRead(pin)
    # You can add assertions to check the result, e.g., if it's a float




if __name__ == "__main__":
    
    print(f"Pybind11 Module Version: {rs.__version__}")
    app = QApplication([]) # needed for SIMgui tests that rely on QApplication instance
    pytest.main(['-v']) # run pytest with verbose output
    sys.exit() # shutdown Qt event loop that was started by QApplication([])
    
