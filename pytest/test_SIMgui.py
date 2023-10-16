import pytest
import sys
import time
sys.path.insert(0,"..\\ATP_Room_Sim") # Add the directory containing the SIMgui.py file to the Python path
from PyQt5.QtWidgets import QApplication
from SIMgui import SIMgui
from room_simulator import Room # New room class and temperature generator
from MockFirmata import MockFirmata # mock arduino class

from constants import * # pin definitions


@pytest.fixture()
def gui():
    # Setup
    SIMroom = Room(temperature=25.0, outside_temperature=30,
                   humidity=20.0, room_dimensions=[10, 10, 2]) 
                                # breedte, lengte, hoogte

    mockFirmata = MockFirmata(Port=3, Room=SIMroom)
    
    pinConnections = [
                f"d:{DHT22_1}:DHT22_1", 
                f"d:{DHT22_2}:DHT22_2",
                f"d:{RELAY_HEATER}:RELAY_HEATER",
                f"d:{RELAY_COOLER}:RELAY_COOLER",
                f"d:{RELAY_SUNSCREEN}:RELAY_SUNSCREEN",
                f"a:{LDR}:LDR",
                ]

    for pin in pinConnections:
        mockFirmata.setPinMode(pin)
    
    gui = SIMgui(MockFirmata=mockFirmata,graphLength=10)
    yield gui
    # Cleanup after the test
    gui.__del__() # removes reactivex subscriptions from threads otherwise test slow down to a halt
    
def test_SIMgui_initialization(gui):
    SIMroom = Room(temperature=25.0, outside_temperature=30,
                   humidity=20.0, room_dimensions=[10, 10, 2]) 
                                # breedte, lengte, hoogte

    mockFirmata = MockFirmata(Port=3, Room=SIMroom)
    gui = SIMgui(MockFirmata=mockFirmata)
    assert gui.room is not None
    # testing default values
    assert gui.target_temperature == 20
    assert gui.PollInterval == 1.0
    assert gui.temp_threshold == 0.5
    assert gui.temperatureValues.maxlen == 10
    

def test_set_target_temperature(gui):
    # Test initial value
    assert gui.target_temperature == 20

    # Set a new target temperature
    gui.setTargetTemperature(25)

    # Test the updated target temperature
    assert gui.target_temperature == 25

# [inside_temp, outside_temp, target_temperature, temp_threshold, heater_state, cooler_state, sunscreen_state, ActiveTempControlEnabled, lux, lux_threshold]
@pytest.mark.parametrize("Command_Args, OutStates", [
    # Test case 0: No commands, all states are initially off
    ([20.0, 25.0, 20.0, 0.5, False, False, False, True, 500, 1000], [False, False, False]),

    # Test case 1: Lux level above the threshold, sunscreen should be on
    ([22.0, 25.0, 22.0, 0.5, False, False, False, True, 1200, 1000], [False, False, True]),

    # Test case 2: Inside temperature below target - threshold, heater should be on
    ([19.0, 25.0, 22.0, 0.5, False, False, False, True, 500, 1000], [True, False, False]),

    # Test case 3: Inside temperature above target + threshold, cooler should be on
    ([23.0, 25.0, 22.0, 0.5, False, False, False, True, 500, 1000], [False, True, False]),

    # Test case 4: Inside temperature within the acceptable range, all states off
    ([22.0, 25.0, 22.0, 0.5, False, False, False, True, 500, 1000], [False, False, False]),

    # Test case 5: Heater is on, inside temperature within the acceptable range, turn off heater
    ([22.0, 25.0, 22.0, 0.5, True, False, False, True, 500, 1000], [False, False, False]),

    # Test case 6: Cooler is on, inside temperature within the acceptable range, turn off cooler
    ([22.0, 25.0, 22.0, 0.5, False, True, False, True, 500, 1000], [False, False, False]),

    # Test case 7: Lux level below the threshold, sunscreen should be off
    ([22.0, 25.0, 22.0, 0.5, False, False, True, True, 800, 1000], [False, False, False]),
    
    # Test case 8: Lux level above the threshold, sunscreen should be on (ActiveTempControlEnabled is False)
    ([22.0, 25.0, 22.0, 0.5, False, False, False, False, 1200, 1000], [False, False, True]),

    # Test case 9: Inside temperature below target - threshold, heater should be off to ensure passive heating (ActiveTempControlEnabled is False)
    ([19.0, 25.0, 22.0, 0.5, False, False, False, False, 500, 1000], [False, False, False]),

    # Test case 10: Inside temperature above target + threshold, cooler should be on (ActiveTempControlEnabled is False)
    ([23.0, 25.0, 22.0, 0.5, False, False, False, False, 500, 1000], [False, True, False]),

    # Test case 11: Inside temperature within the acceptable range, all states off (ActiveTempControlEnabled is False)
    ([22.0, 25.0, 22.0, 0.5, False, False, False, False, 500, 1000], [False, False, False]),

    # Test case 12: Heater is on, inside temperature within the acceptable range, turn off heater (ActiveTempControlEnabled is False)
    ([22.0, 25.0, 22.0, 0.5, True, False, False, False, 500, 1000], [False, False, False]),

    # Test case 13: Cooler is on, inside temperature within the acceptable range, turn off cooler (ActiveTempControlEnabled is False)
    ([22.0, 25.0, 22.0, 0.5, False, True, False, False, 500, 1000], [False, False, False]),

    # Test case 14: Lux level below the threshold, sunscreen should be off (ActiveTempControlEnabled is False)
    ([22.0, 25.0, 22.0, 0.5, False, False, True, False, 800, 1000], [False, False, False]),

])

@pytest.mark.filterwarnings("ignore") # Ignore warnings from rx library caused by fast creating and disposing of observables
def test_generate_commands_functional(gui,Command_Args,OutStates):
    assert gui.generateCommands(*Command_Args) == OutStates
    
    
@pytest.mark.parametrize("Commands", [
    ([True, False, False]), # Turn on the heater
    ([False, True, False]), # Turn on the cooler
    ([False, False, True]), # Turn on the sunscreen
    ([True, True, False]), # Turn on the heater and cooler
    ([False, True, True]), # Turn on the cooler and sunscreen
    ([True, False, True]), # Turn on the heater and sunscreen
    ([True, False, False]), # Turn on the heater
    ([False, False, False])  # Turn off all devices
])

def test_execute_commands(gui,Commands):
    # Test executing commands with different combinations of heater, cooler and sunscreen
    gui.executeCommands(*Commands)
    assert gui.room.isHeaterActive() == Commands[0]
    assert gui.room.isCoolerActive() == Commands[1]
    assert gui.room.isSunscreenActive() == Commands[2]

def test_update_plots(gui):

    # Test updating plots with temperature and humidity values
    gui.updatePlots(22, 60)
    assert gui.temperatureValues[-1] == 22
    assert gui.humidityValues[-1] == 60

    # Test updating plots with temperature and humidity values
    gui.updatePlots(25, 55)
    assert gui.temperatureValues[-1] == 25
    assert gui.humidityValues[-1] == 55

@pytest.mark.parametrize("poll_rate, expected_rate", [
    (1.0, 1.0),  # Test initial poll rate (no change)
    (2.0, 2.0),  # Set a new poll rate to 2.0
    (-1.0, 1.0),  # Test invalid poll rate (negative value, should not change the poll rate)
    (0.0, 1.0),  # Test invalid poll rate (zero value, should not change the poll rate
    (0.5, 0.5),  # Test half values Set a new poll rate to 0.5 
    (0.1, 0.1),  # Test decimal values Set a new poll rate to 0.1
    (0.01, 0.01),  # Test decimal values Set a new poll rate to 0.01
])

def test_set_poll_interval(gui, poll_rate, expected_rate):
    # Test the initial poll rate
    assert gui.PollInterval == 1.0

    # Set the new poll rate
    gui.setPollInterval(poll_rate)

    # Test the updated poll rate
    assert gui.PollInterval == expected_rate

@pytest.mark.parametrize("threshold, expected_threshold", [
    (0.5, 0.5),  # Test initial threshold (no change)
    (0.3, 0.3),  # Set a new threshold to 0.3
    (-1.0, 0.5),  # Test invalid threshold (negative value, should not change the threshold)
    (0.0, 0.5),  # Test invalid threshold (zero value, should not change the threshold
])

def test_set_temp_threshold(gui, threshold, expected_threshold):
    # Test the initial threshold
    assert gui.temp_threshold == 0.5

    # Set the new threshold
    gui.setTempThreshold(threshold)

    # Test the updated threshold
    assert gui.temp_threshold == expected_threshold

def test_purge_graph_data(gui):

    # Add some data to the graph
    gui.temperatureValues.extend([20, 21, 22])
    gui.humidityValues.extend([50, 51, 52])
    # Purge graph data
    gui.purgeGraphData()

    # Test if graph data is empty
    assert len(gui.temperatureValues) == 0
    assert len(gui.humidityValues) == 0


def test_update_observer(gui):
    assert gui.observablePoll is not None

    # Call the method and check if the observer is created/updated
    gui.updateObserver()
    assert gui.observablePoll is not None

    # Call the method again and check if the observer is updated
    previous_poll = gui.observablePoll
    gui.updateObserver()
    assert gui.observablePoll is not None
    assert gui.observablePoll != previous_poll

def test_simulation_gui_system_test(gui):
    
    # Initialize the SIMgui class
    assert isinstance(gui, SIMgui)

    # Check initial values
    assert gui.PollInterval == 1.0
    assert gui.target_temperature == 20
    assert gui.temp_threshold == 0.5

    # Change target temperature
    gui.setTargetTemperature(25)
    assert gui.target_temperature == 25
    
    
    gui.room.setOutsideTemperature(10)
    offset = gui.room.getOutsideTemperature() - 10
    assert gui.room.getOutsideTemperature() == 10 + offset

    # Change poll rate
    gui.setPollInterval(0.2)
    assert gui.PollInterval == 0.2

    # Wait for some time to let the simulation run
    time.sleep(2)
    
    # Check if the plots are being updated
    assert len(gui.temperatureValues) > 0
    assert len(gui.humidityValues) > 0

    # Execute some commands
    gui.executeCommands(True, False, False)
    assert gui.room.isHeaterActive()
    assert not gui.room.isCoolerActive()
    assert not gui.room.isSunscreenActive()

    gui.setPollInterval(2.0) # Set a new poll rate to ennext test will be more accurate
    # Update plots with new temperature and humidity values
    gui.updatePlots(22, 40)
    assert gui.temperatureValues[-1] == 22
    assert gui.humidityValues[-1] == 40

    # Set a new poll rate and check if the observer is updated
    gui.setPollInterval(3.0)
    assert gui.PollInterval == 3.0
    assert len(gui.temperatureValues) == 0
    assert len(gui.humidityValues) == 0
    
    
    # Purge graph data and check if the deques are cleared
    gui.purgeGraphData()
    assert len(gui.temperatureValues) == 0
    assert len(gui.humidityValues) == 0
    
    # Update observer
    gui.updateObserver()
    assert gui.observablePoll is not None


if __name__ == "__main__":
    gui = QApplication([]) # needed for SIMgui tests that rely on QApplication instance
    pytest.main(['-v']) # run pytest with verbose output
    sys.exit() # shutdown Qt event loop that was started by QApplication([])