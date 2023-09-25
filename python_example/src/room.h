// room.h
#pragma once

#include <numeric>
#include <chrono>
#include <vector>
#include <stdexcept>

class Room {
private:
    float outside_temperature;
    float temperature;
    float humidity; // unused in simulation but included for completeness as set value
    float light_level_lux;
    double sensor_accuracy_offset;
    bool heater_active;
    bool cooler_active;
    bool sunscreen_active;
    float heater_power;
    float cooler_power;
    float room_volume;
    float surface_area;
    float air_density;
    float specific_heat;
    std::chrono::steady_clock::time_point last_update_time;
public:
    Room(float temperature = 25.0, float outside_temperature = 30.0, float humidity = 50.0, std::vector<float> room_dimensions = {10.0, 10.0, 2.0})
        : temperature(temperature), humidity(humidity), outside_temperature(outside_temperature) {

        if (room_dimensions.size() != 3) {
            throw std::invalid_argument("Invalid room dimensions. Expected 3, width, length, and height.");
        }

        this->room_volume = std::accumulate(room_dimensions.begin(), room_dimensions.end(), 1.0, std::multiplies<float>());
        this->surface_area = 2 * (room_dimensions[0] * room_dimensions[2] + room_dimensions[1] * room_dimensions[2]);
        this->air_density = 1.225;
        this->specific_heat = 700.0;
        this->last_update_time = std::chrono::high_resolution_clock::now();
        this->heater_active = false;
        this->cooler_active = false;
        this->sunscreen_active = false;
        this->heater_power = 1000.0;
        this->cooler_power = 2000.0;
        this->light_level_lux = 10000.0;
        // assign random value between -0.5 and 0.5 to sensor offset
        this->sensor_accuracy_offset = static_cast <double> (rand()) / static_cast <double> (RAND_MAX) - 0.5; // seed is 1 automatically
    }
    
    float getTemperature();
    void setTemperature(float temperature) { this->temperature = temperature; }

    float getOutsideTemperature();
    void setOutsideTemperature(float temperature) { this->outside_temperature = temperature; }

    float getHumidity() { return humidity; }
    void setHumidity(float humidity) {
        if (humidity < 0.0 || humidity > 100.0) {
            throw std::invalid_argument("Invalid humidity value. Expected a value between 0 and 100.");
        }
        this->humidity = humidity;
    }

    void setLightLevelLux(float light_level_lux) { 
        if (light_level_lux <= 0.0 || light_level_lux > 100000.0) {
            throw std::invalid_argument("Invalid Light level value. Expected a value above 0 and below 100.000 Lux.");
        }
        this->light_level_lux = light_level_lux; 
    }
    float getLightLevelLux() { return light_level_lux; }

    bool isSunscreenActive() { return sunscreen_active; }
    void activateSunscreen(bool isActive) { this->sunscreen_active = isActive; }

    bool isHeaterActive() { return heater_active; }
    void activateHeater(bool isActive) { this->heater_active = isActive; }

    bool isCoolerActive() { return cooler_active; }
    void activateCooler(bool isActive) { this->cooler_active = isActive; }

    float getHeaterPower() { return heater_power; }
    void setHeaterPower(float power) {
        if (power < 0.0f) {
            throw std::invalid_argument("Invalid heater power value. Expected a non-negative value.");
        }
        this->heater_power = power;
    }
    float getCoolerPower() { return cooler_power; }
    void setCoolerPower(float power) {
        if (power < 0.0f) {
            throw std::invalid_argument("Invalid cooler power value. Expected a non-negative value.");
        }
        this->cooler_power = power;
    }
    
    float calculateTempDelta(float delta_time);
    float calculateHeatExchange();
};