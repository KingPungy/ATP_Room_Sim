import pytest
import sys
from PyQt5.QtWidgets import QApplication
sys.path.insert(0,"..\\ATP_CppRoomSim_PyGUI") # Add the directory containing the module.py file to the Python path
from SIMgui import SIMgui

@pytest.fixture
def gui():
    
    gui = SIMgui()
    yield gui
    # Cleanup after the test
    gui.__del__() # removes reactivex subscriptions from threads
    

def test_gui_initialization(gui):
    assert gui.target_temperature == 20
    assert gui.pollRate == 1.0

def test_set_target_temperature(gui):
    gui.setTargetTemperature(25)
    assert gui.target_temperature == 25

def test_set_poll_rate(gui):
    gui.setPollRate(2.0)
    assert gui.pollRate == 2.0

def test_generate_commands(gui):
    gui.room.setOutsideTemperature(10)
    commands = gui.generateCommands(18.5)
    assert commands == [True, False]

def test_execute_commands(gui):
    gui.executeCommands(True, False)
    assert gui.room.isHeaterActive() == True
    assert gui.room.isCoolerActive() == False
    
def test_generate_and_execute_commands(gui):
    gui.room.setOutsideTemperature(10)
    commands = gui.generateCommands(18.5)
    assert commands == [True, False]
    gui.executeCommands(True, False)
    assert gui.room.isHeaterActive() == True
    assert gui.room.isCoolerActive() == False

def test_update_plots(gui):
    gui.updatePlots(20, 50)
    assert len(gui.temperatureValues) == 1
    assert len(gui.humidityValues) == 1

def test_purge_graph_data(gui):
    gui.updatePlots(20, 50)
    gui.purgeGraphData()
    assert len(gui.temperatureValues) == 0
    assert len(gui.humidityValues) == 0
    

if __name__ == "__main__":
    
    
    app = QApplication([]) # needed for SIMgui tests that rely on QApplication instance
    pytest.main(['-v']) # run pytest with verbose flag
    sys.exit() # shutdown qt application after tests are complete
    