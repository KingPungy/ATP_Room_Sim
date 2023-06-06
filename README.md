
## NOTE
things that have to be the same

setup.py

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

src/main.cpp
```py
PYBIND11_MODULE({Module Name}, m) 
...
```

possible files that also require the same name
 - `docs/conf.py`

---
## How to build?
Pybind11 Module build command and folder: 
```python
C:\code\ATP\ATP_Testing_Project\ATP_CppRoomSim_PyGUI>
```

Command: 
```powershell
pip install .\python_example\
```

