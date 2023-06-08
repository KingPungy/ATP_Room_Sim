// room.cpp
#include "room.h"
#include <algorithm>
#include <iostream>


float Room::getTemperature() {
    // Simulate time passing
    auto current_time = std::chrono::high_resolution_clock::now();
    double delta_time = std::chrono::duration_cast<std::chrono::microseconds>(current_time - last_update_time).count() / 1000000.0;
    last_update_time = current_time;
 

    temperature += this->calculateTempDelta(delta_time);
    
    // Ensure temperature stays within a valid range
    temperature = std::clamp(temperature, -40.0f, 80.0f); // based on datasheet of sensor DHT 22 (-40 - +80)
    return temperature + this->sensor_accuracy_offset;
    
}
 
float Room::calculateTempDelta(float delta_time) { 
    // Calculate the change in temperature based on heater and cooler activity
    float internal_temp_change = (delta_time * ((this->heater_active * this->heater_power) - (this->cooler_active * this->cooler_power))) / (
            this->room_volume * this->air_density * this->specific_heat);

    // change the calculation below to lose heat to the outside
    float external_temp_change = this->calculateHeatExchange() * delta_time / (this->room_volume * this->air_density * this->specific_heat);

    float delta_temp = internal_temp_change + external_temp_change;

    return delta_temp;
}

float Room::calculateHeatExchange() { 
    // Calculate the heat exchange between the room and the outside based on the surface area and temperature difference
    float thermal_conductivity_brick = 0.18;  // Thermal conductivity of insulatedbrick (W/m*K)
    float thickness_brick = 0.3;  // Thickness of brick wall (m)
    float temperature_diff = this->temperature - this->outside_temperature;

    // Qw = As*Uc*ΔTemp heat loss via walls heat loss via conduction through brick wall
    float heat_exchange = (this->surface_area * thermal_conductivity_brick * temperature_diff) / thickness_brick;
    
    // print(f"heat_exchange: {heat_exchange}")
    return -heat_exchange; // in watts
}
        