

---
## How to build?
Pybind11 Module build command and folder: 
```python
..\ATP_Room_Sim\
```

Command to install pybind11 module: 
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
