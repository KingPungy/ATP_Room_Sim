import pytest
import sys
import math
from PyQt5.QtWidgets import QApplication
sys.path.insert(0,"..\\ATP_Room_Sim") # Add the directory containing the module.py file to the Python path
from SIMgui import SIMgui
from room_simulator import Room

@pytest.fixture
def gui():
    
    gui = SIMgui()
    yield gui
    # Cleanup after the test
    gui.__del__() # removes reactivex subscriptions from threads
    

def test_gui_initialization(gui):
    # testing default values of SIMgui
    assert gui.target_temperature == 20
    assert gui.PollInterval == 1.0
    assert gui.threshold == 0.5
    assert gui.temperatureValues.maxlen == 10
    
    # test that room is initialized
    assert gui.room is not None
    assert isinstance(gui.room, Room)
    assert gui.observablePoll != None

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

def test_pipeline_to_execute_commands(gui):
    assert gui.temperature_subject != None
    gui.room.setOutsideTemperature(10)
    gui.temperature_subject.on_next(18.5)
    assert gui.room.isHeaterActive() == True
    assert gui.room.isCoolerActive() == False
    gui.temperature_subject.on_next(21.5)
    assert gui.room.isHeaterActive() == False
    assert gui.room.isCoolerActive() == False
    gui.room.setOutsideTemperature(30)
    gui.temperature_subject.on_next(21.5)
    assert gui.room.isHeaterActive() == False
    assert gui.room.isCoolerActive() == True
    
def test_update_plots(gui):
    gui.updatePlots(20, 50)
    assert len(gui.temperatureValues) == 1
    assert len(gui.humidityValues) == 1

def test_purge_graph_data(gui):
    gui.updatePlots(20, 50)
    assert len(gui.temperatureValues) == 1
    assert len(gui.humidityValues) == 1
    gui.purgeGraphData()
    assert len(gui.temperatureValues) == 0
    assert len(gui.humidityValues) == 0
    

def test_connected_ui_functions(gui):
    assert gui.HeaterWattSelectBox.value() == gui.room.getHeaterPower() == 1000
    assert gui.CoolerBTUSelectBox.value() == gui.room.getCoolerPower() == 2000
    assert gui.OutTempSelectBox.value() == math.floor(gui.room.getOutsideTemperature()) == 29
    assert gui.RoomTempSelectBox.value() == math.floor(gui.room.getTemperature()) == 24
    
    

if __name__ == "__main__":
    
    # this file has overlapping tests with test_SIMgui.py for redundancy 
    # some are more elaborate in the othre files
    
    app = QApplication([]) # needed for SIMgui tests that rely on QApplication instance
    pytest.main(['-v']) # run pytest with verbose flag
    sys.exit() # shutdown qt application after tests are complete
    