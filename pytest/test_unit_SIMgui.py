import pytest
import sys
sys.path.insert(0,"..\\ATP_CppRoomSim_PyGUI") # Add the directory containing the module.py file to the Python path
from PyQt5.QtWidgets import QApplication
from SIMgui import SIMgui

@pytest.fixture
def gui():
    # Setup
    gui = SIMgui()
    yield gui
    # Cleanup after the test
    gui.__del__() # removes reactivex subscriptions from threads
    

def test_set_target_temperature(gui):
    # Test initial value
    assert gui.target_temperature == 20

    # Set a new target temperature
    gui.setTargetTemperature(25)

    # Test the updated target temperature
    assert gui.target_temperature == 25

def test_generate_commands(gui):

    # Test with temperature below target temperature and outside temperature below current temperature
    gui.room.setOutsideTemperature(15)
    commands = gui.generateCommands(18)
    assert commands == [True, False]

    # Test with temperature above target temperature and outside temperature above current temperature
    gui.room.setOutsideTemperature(30)
    commands = gui.generateCommands(22)
    assert commands == [False, True]

    # Test with temperature within threshold range and heater active
    gui.room.activateHeater(True)
    commands = gui.generateCommands(20.2)
    assert commands == [False, False]

    # Test with temperature within threshold range and cooler active
    gui.room.activateHeater(False)
    gui.room.activateCooler(True)
    commands = gui.generateCommands(19.8)
    assert commands == [False, False]

def test_execute_commands(gui):

    # Test executing commands to activate heater and deactivate cooler
    gui.executeCommands(True, False)
    assert gui.room.isHeaterActive() == True
    assert gui.room.isCoolerActive() == False

    # Test executing commands to deactivate heater and activate cooler
    gui.executeCommands(False, True)
    assert gui.room.isHeaterActive() == False
    assert gui.room.isCoolerActive() == True

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
    gui.SensorPollRateBox.setValue(1.0)
    gui.setPollRate(2.0)

    # Test the updated poll rate
    assert gui.pollRate == 2.0

def test_set_threshold(gui):

    # Test initial threshold
    assert gui.threshold == 0.5

    # Set a new threshold
    gui.setThreshold(0.3)

    # Test the updated threshold
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

if __name__ == "__main__":
    
    # print(f"Pybind11 Module Version: {rs.__version__}")
    gui = QApplication([]) # needed for SIMgui tests that rely on QApplication instance
    pytest.main(['-v']) # run pytest with verbose output
    sys.exit() # shutdown Qt event loop that was started by QApplication([])