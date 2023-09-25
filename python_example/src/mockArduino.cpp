
#ifndef MOCKARDUINO_H
#define MOCKARDUINO_H

#pragma once

#include "mockArduino.h"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

// initalize all mockArduino functions

mockArduino::mockArduino(int com_Port, Room* room) {
    this->com_Port = com_Port;
    this->room = room;
    this->digitalPins.resize(54, std::make_pair(EMPTY, false)); // 0 - 53 digital pins initialized to empty and false
    this->analogPins.resize(17, EMPTY); // 0 - 16 analog pins initialized to empty 
}

mockArduino::~mockArduino() {
}


void mockArduino::set_pin_mode(int pin_type, int pin_num , int pin_mode) {
    // check if pin is digital or analog
    if (pin_type == 0){
        if (pin_num >= 0 && pin_num <= 53){ // digital
            if ( pin_mode >= 0 && pin_mode <= 5) {
                // set the value of the pin
                this->digitalPins[pin_num].first = pin_mode;
            } else {
                throw std::invalid_argument("Invalid pin mode. Expected a value between 0 and 5.");
            }
        } else {
            throw std::invalid_argument("Invalid pin number. Expected a value between 0 and 53.");
        }
    } else if (pin_type == 1 ){
        if ( 0 <= pin_num && pin_num <= 16) { // analog
            // check if pin is input or output
            if ( pin_mode == 0 || pin_mode == 6) {
                this->analogPins[pin_num] = pin_mode;
            }
            else {
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

void mockArduino::set_digital_pin(int pin_num, bool state){ // digital only
    // check if pin is digital or analog
    if (pin_num >= 0 && pin_num <= 53){
        // check for pin mode error
        if (this->digitalPins[pin_num].first == 0 || (3 <= this->digitalPins[pin_num].first && this->digitalPins[pin_num].first <=5)){
            // set pin state
            this->digitalPins[pin_num].second = state;
        }
        else {
            throw std::invalid_argument("Invalid pin mode. Expected a value of between 0, 3, 4, 5.");
        }

    } else {
        // return error
        throw std::invalid_argument("Invalid pin number. Expected a value between 0 and 53.");
    }
}

std::variant<bool, double, int> mockArduino::get_pin_data(int pin_type, int pin_num, int pin_mode) {

    // check if pin is digital or analog
    if (pin_type == 0 && (pin_num >= 0 && pin_num <= 53) ){
        // check for pin mode error
        if (this->digitalPins[pin_num].first >= 0 && this->digitalPins[pin_num].first <= 5){
            // return the value of the pin
            switch (this->digitalPins[pin_num].first) {
                case 0:
                    return this->digitalPins[pin_num].second;
                    break;
                case 1:
                    return this->read_DHT22_1();
                    break;
                case 2:
                    return this->read_DHT22_2();
                    break;
                case 3:
                    return this->read_Relay_Heater();
                    break;
                case 4:
                    return this->read_Relay_Cooler();
                    break;
                case 5:
                    return this->read_Relay_Sunscreen();
                    break;
                default:
                    throw std::invalid_argument("Invalid pin mode. Expected one of the following values 0, 1, 2, 3, 4, 5.");
                    break;
            }
        }
        else {
            throw std::invalid_argument("Invalid pin mode. Expected one of the following values 0, 1, 2, 3, 4, 5.");
        }
    } else if (pin_type == 1 && ( pin_num >= 0 && pin_num <= 16)) {
        // check if pin is input or output
        if ( pin_mode == 0 || pin_mode == 6) {
            if (this->analogPins[pin_num] == 6){
                return this->read_LDR();
            }
            else {
                throw std::invalid_argument("Invalid pin mode. Expected one of the following  0 or 6.");
            }
        }
        else {
            throw std::invalid_argument("Invalid pin mode. Expected one of the following  0 or 6.");
        }
    }
    else {
        // return error
        throw std::invalid_argument("Invalid pin number and pin type. Expected a value between 0 and 53 for digital pins and 0 and 16 for analog pins.");
        
    }

}


double mockArduino::read_DHT22_1() {
    return this->room->getTemperature();
}

double mockArduino::read_DHT22_2() {
    return this->room->getOutsideTemperature();
}

int mockArduino::read_LDR() { // mocks the LDR sensor GL5528 returning a value between 0 and 1024
    // Get lux value from the sensor (replace this with your actual sensor reading)
    double lux = this->room->getLightLevelLux();

    // Constants for your LDR setup
    const double R10lx = 15000; // Light resistance at 10 lux in ohms
    const double gamma = 0.6;   // Gamma value
    const double R1 = 5000;     // Resistor R1 in ohms
    const double VCC = 5.0;     // Supply voltage in volts

    // Calculate LDR resistance LDR_R using gamma formula
    double LDR_R = pow(10, gamma) * R10lx / pow(lux, gamma);

    // Calculate voltage across photo-resistor
    double voltage = (VCC * R1) / (LDR_R + R1);

    // Map voltage to the range [0, 1024] (assuming a 10-bit ADC)
    int mappedValue = static_cast<int>((voltage / VCC) * 1024);

    return mappedValue;
}


void mockArduino::write_Relay_Heater( bool state) {
    this->room->activateHeater(state);
}

bool mockArduino::read_Relay_Heater() {
    return this->room->isHeaterActive();
}

void mockArduino::write_Relay_Cooler( bool state) {
    this->room->activateCooler(state);
}

bool mockArduino::read_Relay_Cooler() {
    return this->room->isCoolerActive();
}

void mockArduino::write_Relay_Sunscreen( bool state) {
    this->room->activateSunscreen(state);
}

bool mockArduino::read_Relay_Sunscreen() {
    return this->room->isSunscreenActive();
}

#endif // MOCKARDUINO_H