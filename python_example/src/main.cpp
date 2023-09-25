// main.cpp

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "room.h"
#include "mockArduino.h"

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)


namespace py = pybind11;

PYBIND11_MODULE(room_simulator, m) {
    m.doc() = "pybind11 room simulator plugin"; // optional module docstring
    py::class_<Room>(m, "Room")
        .def(py::init<float, float, float, std::vector<float>>(), 
            py::arg("temperature") = 25.0f, 
            py::arg("outside_temperature") = 30.0f, 
            py::arg("humidity") = 50.0f, 
            py::arg("room_dimensions") = std::vector<float>{10.0f, 10.0f, 2.0f})
        .def("getTemperature", &Room::getTemperature)
        .def("setTemperature", &Room::setTemperature, py::arg("temperature"))
        .def("getHumidity", &Room::getHumidity)
        .def("setHumidity", &Room::setHumidity, py::arg("humidity"),py::doc("Set humidity to a value between 0 and 100"))
        .def("getLightLevelLux", &Room::getLightLevelLux)
        .def("setLightLevelLux", &Room::setLightLevelLux, py::arg("light_level_lux"))
        .def("isHeaterActive", &Room::isHeaterActive)
        .def("activateHeater", &Room::activateHeater, py::arg("isActive"))
        .def("isCoolerActive", &Room::isCoolerActive)
        .def("activateCooler", &Room::activateCooler, py::arg("isActive"))
        .def("isSunscreenActive", &Room::isSunscreenActive)
        .def("activateSunscreen", &Room::activateSunscreen, py::arg("isActive"))
        .def("getHeaterPower", &Room::getHeaterPower)
        .def("setHeaterPower", &Room::setHeaterPower, py::arg("power"))
        .def("getCoolerPower", &Room::getCoolerPower)
        .def("setCoolerPower", &Room::setCoolerPower, py::arg("power"))
        .def("getOutsideTemperature", &Room::getOutsideTemperature)
        .def("setOutsideTemperature", &Room::setOutsideTemperature, py::arg("temperature"))
        .def("calculateTempDelta", &Room::calculateTempDelta, py::arg("delta_time"))
        .def("calculateHeatExchange", &Room::calculateHeatExchange);
    
    py::class_<mockArduino>(m, "mockArduino")
        .def(py::init<int, Room*>(), 
            py::arg("com_Port") = 3, 
            py::arg("room") = nullptr )
        .def("get_com_Port", &mockArduino::get_com_Port)
        .def("get_room", &mockArduino::get_room)
        .def("read_DHT22_1", &mockArduino::read_DHT22_1)
        .def("read_DHT22_2", &mockArduino::read_DHT22_2)
        .def("read_LDR", &mockArduino::read_LDR)
        .def("write_Relay_Heater", &mockArduino::write_Relay_Heater, py::arg("state"))
        .def("read_Relay_Heater", &mockArduino::read_Relay_Heater)
        .def("write_Relay_Cooler", &mockArduino::write_Relay_Cooler, py::arg("state"))
        .def("read_Relay_Cooler", &mockArduino::read_Relay_Cooler)
        .def("write_Relay_Sunscreen", &mockArduino::write_Relay_Sunscreen, py::arg("state"))
        .def("read_Relay_Sunscreen", &mockArduino::read_Relay_Sunscreen)
        .def("set_digital_pin", &mockArduino::set_digital_pin, py::arg("pin_num"), py::arg("state"))
        .def("set_pin_mode", &mockArduino::set_pin_mode, py::arg("pin_type"), py::arg("pin_num"), py::arg("pin_mode"))
        .def("get_pin_data", &mockArduino::get_pin_data, py::arg("pin_type"), py::arg("pin_num"), py::arg("pin_mode"));
    // #ifdef VERSION_INFO;
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
    // #else
        // m.attr("__version__") = "dev";
    // #endif


}

