// room.h

#include <numeric>
#include <chrono>
#include <vector>
#include <stdexcept>

class Room {
private:
    float temperature;
    float humidity;
    double sensor_accuracy_offset;
    bool heater_active;
    bool cooler_active;
    float heater_power;
    float cooler_power;
    float room_volume;
    float surface_area;
    float air_density;
    float specific_heat;
    std::chrono::steady_clock::time_point last_update_time;
    float outside_temperature;
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
        this->heater_power = 1000.0;
        this->cooler_power = 2000.0;
        // assign random value between -0.5 and 0.5 to sensor offset
        this->sensor_accuracy_offset = static_cast <double> (rand()) / static_cast <double> (RAND_MAX) - 0.5; // seed is 1 automatically
    }
    
    float getTemperature();
    void setTemperature(float temperature) { this->temperature = temperature; }
    float getHumidity() { return humidity; }
    void setHumidity(float humidity) {
        if (humidity < 0.0 || humidity > 100.0) {
            throw std::invalid_argument("Invalid humidity value. Expected a value between 0 and 100.");
        }
        this->humidity = humidity;
    }
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
    float getOutsideTemperature();
    void setOutsideTemperature(float temperature) { this->outside_temperature = temperature; }
    
    float calculateTempDelta(float delta_time);
    float calculateHeatExchange();
};