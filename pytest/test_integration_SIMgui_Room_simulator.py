import pytest
import sys
import math
from PyQt5.QtWidgets import QApplication
sys.path.insert(0,"..\\ATP_Room_Sim") # Add the directory containing the module.py file to the Python path
from SIMgui import SIMgui
from room_simulator import Room # New room class and temperature generator
from MockFirmata import MockFirmata # mock arduino class

from constants import * # pin definitions
from test_SIMgui import gui


def test_gui_initialization(gui):
    # testing default values of SIMgui
    assert gui.target_temperature == 20
    assert gui.PollInterval == 1.0
    assert gui.temp_threshold == 0.5
    assert gui.temperatureValues.maxlen == 10
    
    # test that room is initialized
    assert gui.room is not None
    assert isinstance(gui.room, Room)
    assert gui.observablePoll != None

 # data object is als volgt opgebouwd: [[inside_temp, inside_humid], [outside_temp, outside_humid], light_level_lux]
@pytest.mark.parametrize("input_data, output_states, additionalSettings", [
    ([[18.5, 50], [10, 50], 500], [True, False, False],[20,0.5,10000,False]),  # Low outside temperature, heater active
    ([[21.5, 50], [10, 50], 500], [False, False, False],[20,0.5,10000,False]),  # Low outside temperature, heater deactivated
    ([[21.5, 50], [30, 50], 500], [False, True, False],[20,0.5,10000,False]),  # High outside temperature, cooler active
    ([[10.0, 50], [10, 50], 12000], [True, False, True],[20,0.5,10000,False]),  # Low outside temperature, heater active, sunscreen active
    ([[22.0, 50], [30, 50], 500], [False, True, False],[20,0.5,10000,False]),  # High outside temperature, cooler active
    ([[24.0, 50], [25, 50], 30000], [False, True, True],[20,0.5,10000,False]),  # Moderate outside temperature, sunscreen active
    ([[24.0, 50], [10, 50], 500], [False, True, False],[20,0.5,10000,True]),  # Low outside temperature, Activetemp control, cooler active
    ([[10.0, 50], [40, 50], 500], [True, False, False],[20,0.5,10000,True]),  # High outside temperature, Activetemp control, Heater active
    ([[20.0, 50], [20, 50], 500], [False, False, False],[20,0.5,10000,False]),  # Equal inside and outside temperatures as target temp, everything off
])

def test_pipeline_to_execute_commands(gui,input_data, output_states,additionalSettings):
    # make sure the subject is not None
    assert gui.temperature_light_subject != None
   
    # default values that are implied for this test
    gui.target_temperature = additionalSettings[0]
    gui.temp_threshold = additionalSettings[1]
    gui.lux_threshold = additionalSettings[2]
    gui.ActiveTempControlCheckBox.setChecked(additionalSettings[3])
    
    gui.temperature_light_subject.on_next(input_data)
    # check if the commands are generated and executed correctly
    assert gui.room.isHeaterActive() == output_states[0]
    assert gui.room.isCoolerActive() == output_states[1]
    assert gui.room.isSunscreenActive() == output_states[2]
    

def test_connected_ui_functions(gui):
    assert gui.HeaterWattSelectBox.value() == gui.room.getHeaterPower() == 1000
    assert gui.CoolerBTUSelectBox.value() == gui.room.getCoolerPower() == 2000
    assert gui.ActiveTempControlCheckBox.isChecked() == False
    assert gui.LuxThreshSelectBox.value() == 10000
    assert gui.TargetThreshSelectBox.value() == 0.5
    assert gui.SensorPollIntervalBox.value() == 1.0
    assert gui.TargetTempSelectBox.value() == 20
    assert gui.HeaterStateBox.isChecked() == False
    assert gui.CoolerStateBox.isChecked() == False
    assert gui.SunscreenStateBox.isChecked() == False
    assert gui.OutTempSelectBox.value() == round(gui.room.getOutsideTemperature()) == 30
    assert gui.RoomTempSelectBox.value() == round(gui.room.getTemperature()) == 25
    
    

if __name__ == "__main__":
    
    # this file has overlapping tests with test_SIMgui.py for redundancy 
    # some are more elaborate in the other files
    
    app = QApplication([]) # needed for SIMgui tests that rely on QApplication instance
    pytest.main(['-v']) # run pytest with verbose flag
    sys.exit() # shutdown qt application after tests are complete
    