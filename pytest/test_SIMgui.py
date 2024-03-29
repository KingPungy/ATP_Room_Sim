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

# Ignore warnings from rx library caused by fast creating and disposing of observables 
# because pytest can't reuse the same class for some reason
@pytest.mark.filterwarnings("ignore") 
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


@pytest.mark.parametrize("lux_threshold, expected_threshold", [
    (1,1), # should work
    (-1,10000), # should not work
    (500,500), # should work
    (10000,10000), # should work
    (0,10000), # should not work
    (100001,100001), # should work but has no effect because it is out of range of the LDR
    ])

def test_lux_threshold(gui,lux_threshold,expected_threshold):
    # Test the initial threshold
    assert gui.lux_threshold == 10000

    # Set the new threshold
    gui.setLuxThreshold(lux_threshold)
    # Test the updated threshold
    assert gui.lux_threshold == expected_threshold

@pytest.mark.parametrize("expected_lux,max_error", [
    (1000,0.06),
    (2000,0.06),
    (3000,0.06),	
    (5000,0.06),
    (10000,0.06),
    (15000,0.06),
    (25000,0.06),
    (40000,0.06),
    (50000,0.06),
    (60000,0.06),
    (70000,0.06),
    (80000,0.06),
    (90000,0.06),
    (99999,0.1), # end of conversion spectrum has most error due to logarithmic nature of the conversion and the precision of the ADC conversion
])

def test_lux_calculation(gui,expected_lux,max_error):
    # Test the initial lux level
    assert gui.room.getLightLevelLux() == 10000
    gui.room.setLightLevelLux(expected_lux)
    assert gui.calculateLuxFromADC(gui.firmata.analogRead(LDR)) == pytest.approx(expected_lux, max_error)


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
    assert gui.lux_threshold == 10000

    # Change target temperature
    gui.setTargetTemperature(25)
    assert gui.target_temperature == 25
    
    # check if the outside temp is correct
    gui.room.setOutsideTemperature(10)
    offset = gui.room.getOutsideTemperature() - 10
    assert gui.room.getOutsideTemperature() == 10 + offset

    # Change poll rate
    gui.setPollInterval(0.2)
    assert gui.PollInterval == 0.2


    gui.setLuxThreshold(20000) # de gebruiker vind een beetje zon niet erg maar wil niet dat het te warm wordt vanwege de zon

    gui.room.setLightLevelLux(50000) # the sun starts shining outside
    gui.room.setOutsideTemperature(40) # het wordt erg warm buiten
    gui.room.setTemperature(30) # it is somehow very hot inside right now

    # Wait for some time to let the simulation run
    time.sleep(2)
    
    # Check if the plots are being updated
    assert len(gui.temperatureValues) > 0
    assert len(gui.humidityValues) > 0

    # de verwachte state van het regelsysteem is dat de heater uit is, de cooler aan is en de sunscreen aan is
    assert not gui.room.isHeaterActive()
    assert gui.room.isCoolerActive()
    assert gui.room.isSunscreenActive()

    gui.room.setLightLevelLux(100) # the sun stops shining outside
    gui.room.setOutsideTemperature(5) # het wordt koud buiten

    # Wait for some time to let the simulation run
    time.sleep(2)
    assert not gui.room.isHeaterActive()
    assert not gui.room.isCoolerActive()
    assert not gui.room.isSunscreenActive()


    gui.setPollInterval(0) # de gebruiker probeert de poll interval op 0 te zetten maar dit mag niet
    assert gui.PollInterval == 0.2 # de poll interval is niet veranderd
    gui.setPollInterval(0.5) # de gebruiker probeert de poll interval op 0.5 te zetten
    assert gui.PollInterval == 0.5 # de poll interval is nu 0.5
    assert len(gui.temperatureValues) == 0 # de grafiek is gereset
    assert len(gui.humidityValues) == 0 # de grafiek is gereset

    gui.setLuxThreshold(0) # de gebruiker probeert de lux threshold op 0 te zetten maar dit mag niet
    assert gui.lux_threshold == 20000 # de lux threshold is niet veranderd
    gui.setLuxThreshold(2000) # de gebruiker probeert de lux threshold op 1000 te zetten
    assert gui.lux_threshold == 2000 # de lux threshold is nu 1000


    # het is nu heel warm binnen maar de koeling gaat niet aan omdat het buiten koud is
    gui.ActiveTempControlCheckBox.setChecked(True) # de gebruiker wil nu dat de koeling wel aan gaat ook als het buiten koud genoeg is voor passieve koeling
    # Wait for some time to let the simulation run
    time.sleep(2)

    assert not gui.room.isHeaterActive()
    assert gui.room.isCoolerActive()
    assert not gui.room.isSunscreenActive()

    gui.setPollInterval(2.0) # Set a new poll rate to on_next test will be more accurate
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