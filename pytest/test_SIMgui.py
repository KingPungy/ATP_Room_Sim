import pytest
import sys
import time
sys.path.insert(0,"..\\ATP_Room_Sim") # Add the directory containing the SIMgui.py file to the Python path
from PyQt5.QtWidgets import QApplication
from SIMgui import SIMgui

@pytest.fixture
def gui():
    # Setup
    gui = SIMgui()
    yield gui
    # Cleanup after the test
    gui.__del__() # removes reactivex subscriptions from threads
    
def test_SIMgui_initialization(gui):
    gui = SIMgui(SIMroom=None)
    assert gui.room is not None
    # testing default values
    assert gui.target_temperature == 20
    assert gui.pollRate == 1.0
    assert gui.threshold == 0.5
    assert gui.temperatureValues.maxlen == 10
    

def test_set_target_temperature(gui):
    # Test initial value
    assert gui.target_temperature == 20

    # Set a new target temperature
    gui.setTargetTemperature(25)

    # Test the updated target temperature
    assert gui.target_temperature == 25

def test_generate_commands(gui):

    assert gui.target_temperature == 20
    assert gui.threshold == 0.5
    assert gui.threshold/2 == 0.25

    # Test case 1: Low temperature, outside temperature lower than room temperature
    gui.room.setOutsideTemperature(15)
    commands = gui.generateCommands(18)
    assert commands == [True, False]

    # Test case 2: High temperature, outside temperature higher than room temperature
    gui.room.setOutsideTemperature(30)
    commands = gui.generateCommands(22)
    assert commands == [False, True]

    # Test case 3: Temperature within threshold range and heater active
    gui.room.activateHeater(True)
    commands = gui.generateCommands(20.2)
    assert commands == [False, False]

    # Test case 4: Temperature within threshold range and cooler active
    gui.room.activateHeater(False)
    gui.room.activateCooler(True)
    commands = gui.generateCommands(19.8)
    assert commands == [False, False]
    
    # Test case 5: Temperature within threshold range and heater and cooler inactive
    gui.room.activateCooler(False)
    commands = gui.generateCommands(19.8)
    assert commands == [False, False]

def test_execute_commands(gui):

    # Test executing commands to activate heater and deactivate cooler
    gui.executeCommands(True, False)
    assert gui.room.isHeaterActive() == True
    assert gui.room.isCoolerActive() == False
    assert gui.HeaterStateBox.isChecked() == True
    assert gui.CoolerStateBox.isChecked() == False

    # Test executing commands to deactivate heater and activate cooler
    gui.executeCommands(False, True)
    assert gui.room.isHeaterActive() == False
    assert gui.room.isCoolerActive() == True
    assert gui.HeaterStateBox.isChecked() == False
    assert gui.CoolerStateBox.isChecked() == True
    
    # Test executing commands to deactivate heater and cooler
    gui.executeCommands(False, False)
    assert gui.room.isHeaterActive() == False
    assert gui.room.isCoolerActive() == False
    assert gui.HeaterStateBox.isChecked() == False
    assert gui.CoolerStateBox.isChecked() == False

def test_update_plots(gui):

    # Test updating plots with temperature and humidity values
    gui.updatePlots(22, 60)
    assert gui.temperatureValues[-1] == 22
    assert gui.humidityValues[-1] == 60

    # Test updating plots with temperature and humidity values
    gui.updatePlots(25, 55)
    assert gui.temperatureValues[-1] == 25
    assert gui.humidityValues[-1] == 55

def test_set_poll_rate(gui):
    # Test initial poll rate
    assert gui.pollRate == 1.0
    # Set a new poll rate
    gui.setPollRate(2.0)
    # Test the updated poll rate
    assert gui.pollRate == 2.0
    # test invalid poll rate
    gui.setPollRate(-1.0)
    assert gui.pollRate == 2.0

def test_set_threshold(gui):

    # Test initial threshold
    assert gui.threshold == 0.5

    # Test new threshold
    gui.setThreshold(0.3)
    # test the updated threshold
    assert gui.threshold == 0.3
    
    # test invalid threshold
    gui.setThreshold(-1.0)
    assert gui.threshold == 0.3

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
    assert gui.pollRate == 1.0
    assert gui.target_temperature == 20
    assert gui.threshold == 0.5

    # Change target temperature
    gui.setTargetTemperature(25)
    assert gui.target_temperature == 25
    
    
    gui.room.setOutsideTemperature(10)
    offset = gui.room.getOutsideTemperature() - 10
    assert gui.room.getOutsideTemperature() == 10 + offset

    # Change poll rate
    gui.setPollRate(0.5)
    assert gui.pollRate == 0.5

    # Wait for some time to let the simulation run
    time.sleep(5)
    
    # Check if the plots are being updated
    assert len(gui.temperatureValues) > 0
    assert len(gui.humidityValues) > 0

    # Execute some commands
    gui.executeCommands(True, False)
    assert gui.room.isHeaterActive()
    assert not gui.room.isCoolerActive()

    # Update plots with new temperature and humidity values
    gui.updatePlots(22, 40)
    assert gui.temperatureValues[-1] == 22
    assert gui.humidityValues[-1] == 40

    # Set a new poll rate and check if the observer is updated
    gui.setPollRate(3.0)
    assert gui.pollRate == 3.0
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