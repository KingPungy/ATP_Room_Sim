
#ifndef MOCKARDUINO_H
#define MOCKARDUINO_H

// #pragma once

#include "mockArduino.h"
#include <variant> // std::variant<>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

// initalize all mockArduino functions

// Function: mockArduino constructor
// Arguments: com_Port (int) - the com port of the arduino
//            room (Room*) - the room object
// Return Type: mockArduino class object
mockArduino::mockArduino(int com_Port, Room* room) {
    this->com_Port = com_Port;
    this->room = room;
    this->digitalPins.resize(54, std::make_pair(EMPTY, false)); // 0 - 53 digital pins initialized to empty and false
    this->analogPins.resize(17, EMPTY); // 0 - 16 analog pins initialized to empty 
}

mockArduino::~mockArduino() {
}


// Function: set_pin_mode
// Arguments: pin_type (int) - the type of pin (digital or analog)
//            pin_num (int) - the number of the pin
//            pin_mode (int) - the mode of the pin
// Return Type: void
void mockArduino::set_pin_mode(int pin_type, int pin_num , int pin_mode) {
    // check if pin is digital or analog
    if (pin_type == 0) {
        if (pin_num >= 0 && pin_num <= 53) { // digital
            if ( pin_mode >= 0 && pin_mode <= 5) {
                // set the value of the pin
                this->digitalPins[pin_num].first = pin_mode;
            } else {
                throw std::invalid_argument("Invalid pin mode. Expected a value between 0 and 5.");
            }
        } else {
            throw std::invalid_argument("Invalid pin number. Expected a value between 0 and 53.");
        }
    } else if (pin_type == 1) {
        if (0 <= pin_num && pin_num <= 16) { // analog
            // check if pin is input or output
            if ( pin_mode == 0 || pin_mode == 6) {;
                this->analogPins[pin_num] = pin_mode;
            } else {
                throw std::invalid_argument("Invalid pin mode. Expected one of the following 0 or 6.");
            }
        } else {
            throw std::invalid_argument("Invalid pin number. Expected a value between 0 and 16.");
        }
    } else {
        // return error
        throw std::invalid_argument("Invalid pin number and pin type. Expected a value between 0 and 53 for digital pins and 0 and 16 for analog pins.");
        
    }
    
}


// Function: set_digital_pin
// Arguments: pin_num (int) - the number of the pin
//            state (bool) - the state of the pin (HIGH or LOW)
// summary: sets the state of the pin. if the pin is a relay, it will set the state of the relay using the room object
// Return Type: void
void mockArduino::set_digital_pin(int pin_num, bool state){ // digital only
    // check if pin is digital or analog
    if (pin_num >= 0 && pin_num <= 53){
        // check for pin mode error
        if (this->digitalPins[pin_num].first == 0 || (3 <= this->digitalPins[pin_num].first && this->digitalPins[pin_num].first <=5)){
            // set pin state
            switch (this->digitalPins[pin_num].first) {
                case EMPTY: // 0
                    this->digitalPins[pin_num].second = state; 
                    break;
                case RELAY_HEATER: // 3
                    this->write_Relay_Heater(state);
                    break;
                case RELAY_COOLER: // 4
                    this->write_Relay_Cooler(state);
                    break;
                case RELAY_SUNSCREEN: // 5
                    this->write_Relay_Sunscreen(state);
                    break;            
                default: // should never happen
                    throw std::invalid_argument("Invalid pin mode. Expected a value of between 0, 3, 4, 5.");
                    break;
            }
        }
        else {
            throw std::invalid_argument("Invalid pin mode. Expected a value of between 0, 3, 4, 5.");
        }

    } else {
        // return error
        throw std::invalid_argument("Invalid pin number. Expected a value between 0 and 53.");
    }
}


// Function: get_pin_data
// Arguments: pin_type (int) - the type of pin (digital or analog)
//            pin_num (int) - the number of the pin
// Return Type: std::variant<bool, double, int> - depending on the pin type and mode
std::variant<bool, double,std::vector<double>, int> mockArduino::get_pin_data(int pin_type, int pin_num) {

    // check if pin is digital or analog
    if (pin_type == 0 && (pin_num >= 0 && pin_num <= 53) ){ // pin is digital
        // check for pin mode error
        if (this->digitalPins[pin_num].first >= 0 && this->digitalPins[pin_num].first <= 5){
            // return the value of the pin
            switch (this->digitalPins[pin_num].first) {
                case EMPTY: // 0
                    return this->digitalPins[pin_num].second;
                    break;
                case DHT22_1: // 1
                    return this->read_DHT22_1();
                    break;
                case DHT22_2: // 2
                    return this->read_DHT22_2();
                    break;
                case RELAY_HEATER: // 3
                    return this->read_Relay_Heater();
                    break;
                case RELAY_COOLER: // 4
                    return this->read_Relay_Cooler();
                    break;
                case RELAY_SUNSCREEN: // 5
                    return this->read_Relay_Sunscreen();
                    break;
                default: // should never happen
                    throw std::invalid_argument("Invalid pin mode. Expected one of the following values 0, 1, 2, 3, 4, 5.");
                    break;
            }
        } else {
            throw std::invalid_argument("Invalid pin mode. Expected one of the following values 0, 1, 2, 3, 4, 5.");
        }
    } else if (pin_type == 1 && ( pin_num >= 0 && pin_num <= 16)) { // pin is analog
        // check if pin is input or output
        if (this->analogPins[pin_num] == LDR){
            return this->read_LDR();
        } else {
            throw std::invalid_argument("Invalid pin mode of given pin. Expected 6 for LDR.");
        }
    } else {
        // return error
        throw std::invalid_argument("Invalid pin number and pin type. Expected a value between 0 and 53 for digital pins and 0 and 16 for analog pins."); 
    }
}

// Function: read_DHT22_1
// Arguments: None
// Return Type: std::vector<double> - the temperature of the room and the humidity of the room	
std::vector<double> mockArduino::read_DHT22_1() {
    std::vector<double> roomTemp = {this->room->getTemperature(), this->room->getHumidity()};
    return roomTemp;
}

// Function: read_DHT22_2
// Arguments: None
// Return Type: std::vector<double> - the temperature outside the room and the humidity outside the room wich is the same as the room
std::vector<double> mockArduino::read_DHT22_2() { 
    std::vector<double> outsideTemp = {this->room->getOutsideTemperature(), this->room->getHumidity()};
    return outsideTemp;
}

// Function: calculateLDRResistance
// Arguments: lux (double) - the light level in the room between 0 and 1024 
//            R10lx (double) - Light resistance at 10 lux in ohms 
//            gamma (double) - Gamma value found in the datasheet
// Return Type: double - the resistance of the LDR in ohms
double calculateLDRResistance(double lux, double R10lx, double gamma) {
    return pow(10, gamma) * R10lx / pow(lux, gamma);
}

// Function: read_LDR
// Arguments: None
// Return Type: int - the light level in the room between 0 and 1024
int mockArduino::read_LDR() {
    // Get lux value from the sensor (replace this with your actual sensor reading)
    double lux = this->room->getLightLevelLux();

    // Constants for your LDR setup
    const double R10lx = 15000; // Light resistance at 10 lux in ohms
    const double gamma = 0.6;   // Gamma value
    const double R1 = 5000;     // Resistor R1 in ohms
    const double VCC = 5.0;     // Supply voltage in volts

    // Calculate LDR resistance LDR_R using gamma formula
    double LDR_R = calculateLDRResistance(lux, R10lx, gamma);

    // Calculate voltage across photo-resistor
    double voltage = (VCC * R1) / (LDR_R + R1);

    // Map voltage to the range [0, 1024] (assuming a 10-bit ADC)
    int mappedValue = static_cast<int>((voltage / VCC) * 1024);

    return mappedValue;
}

// Function: write_Relay_Heater
// Arguments: state (bool) - the state of the heater
// Return Type: void
void mockArduino::write_Relay_Heater( bool state) {
    this->room->activateHeater(state);
}

// Function: read_Relay_Heater
// Arguments: None
// Return Type: bool - the state of the heater
bool mockArduino::read_Relay_Heater() {
    return this->room->isHeaterActive();
}

// Function: write_Relay_Cooler
// Arguments: state (bool) - the state of the cooler
// Return Type: void
void mockArduino::write_Relay_Cooler( bool state) {
    this->room->activateCooler(state);
}

// Function: read_Relay_Cooler
// Arguments: None
// Return Type: bool - the state of the cooler
bool mockArduino::read_Relay_Cooler() {
    return this->room->isCoolerActive();
}

// Function: write_Relay_Sunscreen
// Arguments: state (bool) - the state of the sunscreen
// Return Type: void
void mockArduino::write_Relay_Sunscreen( bool state) {
    this->room->activateSunscreen(state);
}

// Function: read_Relay_Sunscreen
// Arguments: None
// Return Type: bool - the state of the sunscreen
bool mockArduino::read_Relay_Sunscreen() {
    return this->room->isSunscreenActive();
}

#endif // MOCKARDUINO_H