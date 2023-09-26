
#pragma once
#include "room.h"
// #include <iostream>

#include <vector> // std::vector<>
#include <utility> // std::pair<>
#include <variant> // std::variant<>

#define EMPTY 0
// definitions for the sake of the mock
// digital only
#define DHT22_1 1
#define DHT22_2 2
#define RELAY_HEATER 3
#define RELAY_COOLER 4
#define RELAY_SUNSCREEN 5
// analog only
#define LDR 6





class mockArduino {
private:
    /* data */

    int com_Port = 3;
    // digital pin mode, pin state
    std::vector<std::pair<int, bool>> digitalPins;
    // analog pin mode
    std::vector<int> analogPins;
    // room object
    Room* room = nullptr;


public:

    mockArduino(int com_Port,Room* room);
    ~mockArduino();

    int get_com_Port() { return com_Port; }
    Room* get_room() { return room; }

    double read_DHT22_1();
    double read_DHT22_2();
    int read_LDR();

    void write_Relay_Heater(bool state);
    bool read_Relay_Heater();
    void write_Relay_Cooler(bool state);
    bool read_Relay_Cooler();
    void write_Relay_Sunscreen(bool state);
    bool read_Relay_Sunscreen();


    void set_digital_pin(int pin_num, bool state);

    void set_pin_mode(int pin_type, int pin_num, int pin_mode);
    
    std::variant<bool, double, int> get_pin_data(int pin_type, int pin_num); // check if pin is digital or analog an the mode of the pin, input or output
    
};



