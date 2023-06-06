// main.cpp

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "room.h"

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
        .def("isHeaterActive", &Room::isHeaterActive)
        .def("activateHeater", &Room::activateHeater, py::arg("isActive"))
        .def("isCoolerActive", &Room::isCoolerActive)
        .def("activateCooler", &Room::activateCooler, py::arg("isActive"))
        .def("getHeaterPower", &Room::getHeaterPower)
        .def("setHeaterPower", &Room::setHeaterPower, py::arg("power"))
        .def("getCoolerPower", &Room::getCoolerPower)
        .def("setCoolerPower", &Room::setCoolerPower, py::arg("power"))
        .def("getOutsideTemperature", &Room::getOutsideTemperature)
        .def("setOutsideTemperature", &Room::setOutsideTemperature, py::arg("temperature"))
        .def("calculateTempDelta", &Room::calculateTempDelta, py::arg("delta_time"))
        .def("calculateHeatExchange", &Room::calculateHeatExchange);

    // #ifdef VERSION_INFO;
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
    // #else
        // m.attr("__version__") = "dev";
    // #endif


}

