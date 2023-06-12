# ATP Room temperature control simulation
This project is a simulation of a room temperature control system.   
The room is simulated in a C++ Pybind11 module and the control system is simulated in python.   
It uses a PyQt5 GUI to display the temperature and actuator.

Simulated sensors and actuators:
- Temperature/Humidity sensor DHT22
- Generic Heater and Cooler actuators
    - The actuators are simulated by a simple on/off switch
    - The actuators can be set to a specifiec Wattage and BTU

UI Features:
- PyQt5 GUI designed in Qt Designer
- Displays the current temperature and humidity
- Displays the current state of the actuators
- Allows user to set:
    - Target temperature
    - Target Threshold
    - Outside temperature
    - Inside temperature
    - Sensor polling rate


Example of the PyQt5 UI:  
![UI](Img\ExampleUI.png)


---
## How to build? / Setup
Pybind11 Module build command and folder: 
```python
..\ATP_Room_Sim\
```

Command to install C++ Room Simulator pybind11 module:   
Run the following command in the ATP_Room_Sim folder
```powershell
pip install .\python_example\
```
Install requirements for the python code:
```
pip install -r requirements.txt
```

---	

## How to run
```python
python main.py {--verbose} {--log-output} {--log-time}
```

Optional command line arguments:
 - `--verbose` - prints out all executed functions
 - `--log-output` - prints the results of all functions with a return value
 - `--log-time` - prints the excution time of all functions
---
## How to test

Run one of the test_*.py files inside the `ATP_Room_Sim\pytest` folder.  
The rest will be done automatically

Total amount of tests: 36   
Latest results: ``36 passed, 0 skipped, 0 failed in 9.20 seconds``

---
## NOTE for alterations
Things that have to be the same for the pybind module

python_example\setup.py file:

```python
ext_modules = [
    Pybind11Extension("{Module Name}",
    )
]
...

setup(
    name= "{Module Name}"
)
```

python_example\src\main.cpp
```py
PYBIND11_MODULE({Module Name}, m) 
...
```

possible files that also require the same name
 - `docs/conf.py`
