import pytest
import time
import sys
sys.path.insert(0,"..\\ATP_CppRoomSim_PyGUI") # Add the directory containing the module.py file to the Python path
from PyQt5.QtWidgets import QApplication
from SIMgui import SIMgui


# @pytest.
def test_simulation_gui():
    # Create an instance of SIMgui
    sim_gui = SIMgui()

    # Check initial values
    assert sim_gui.pollRate == 1.0
    assert sim_gui.target_temperature == 20

    # Change target temperature
    sim_gui.setTargetTemperature(25)
    assert sim_gui.target_temperature == 25

    # Change poll rate
    sim_gui.setPollRate(0.5)
    assert sim_gui.pollRate == 0.5

    # Wait for some time to let the simulation run
    time.sleep(5)
    
    # Check if the plots are being updated
    assert len(sim_gui.temperatureValues) > 0
    assert len(sim_gui.humidityValues) > 0

    # Execute some commands
    sim_gui.executeCommands(True, False)
    assert sim_gui.room.isHeaterActive()
    assert not sim_gui.room.isCoolerActive()

    # Update plots with new temperature and humidity values
    sim_gui.updatePlots(22, 40)
    assert sim_gui.temperatureValues[-1] == 22
    assert sim_gui.humidityValues[-1] == 40

    # Set a new poll rate and check if the observer is updated
    sim_gui.setPollRate(3.0)
    assert sim_gui.pollRate == 3.0
    assert len(sim_gui.temperatureValues) == 0
    assert len(sim_gui.humidityValues) == 0
    
    
    # Purge graph data and check if the deques are cleared
    sim_gui.purgeGraphData()
    assert len(sim_gui.temperatureValues) == 0
    assert len(sim_gui.humidityValues) == 0



if __name__ == "__main__":
    
    # print(f"Pybind11 Module Version: {rs.__version__}")
    gui = QApplication([]) # needed for SIMgui tests that rely on QApplication instance
    pytest.main(['-v']) # run pytest with verbose output
    sys.exit() # shutdown Qt event loop that was started by QApplication([])