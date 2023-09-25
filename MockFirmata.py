# This file contains the class that mocks the Arduino Firmata library for testing purposes
import pyfirmata
import room_simulator as rs
import time

# pin modes
EMPTY = 0 # will produce error if data is requested
# digital only
DHT22_1 = 1
DHT22_2 = 2
RELAY_HEATER = 3
RELAY_COOLER = 4
RELAY_SUNSCREEN = 5
# analog only
LDR = 6


class MockFirmata:
    def __init__(self,Port='COM3') -> None:
        self.port = Port
        self.MockArduino = rs.mockArduino("COM3")
    
    def begin(self) -> bool:
        if self.MockArduino.get_com_port() == self.port:
            return True
        else:
            Exception("MockArduino not connected to port")
            return False
    
    def digitalWrite(self, pin, value):
        self._digital_read_value = value
        self._room_simulator.digitalWrite(pin, value)
        
    def digitalRead(self, pin): # for DHT22 sensors and actuator relays 
        return self._room_simulator.digitalRead(pin)
    
    def analogWrite(self, pin, value):
        self._analog_read_value = value
        self._room_simulator.analogWrite(pin, value)
        
    def analogRead(self, pin):
        return self._room_simulator.analogRead(pin)


# Testing
# ===========================================================

room = rs.Room(temperature=25.0, outside_temperature=30,
                   humidity=20.0, room_dimensions=[10, 10, 2])



mocky = rs.mockArduino(3, room) # COM3 port and room object
print(mocky.get_com_Port()) # COM3


mocky.set_pin_mode(0,7,DHT22_1) # pin D7 is DHT22_1
mocky.set_pin_mode(1,0,LDR) # pin A0 is LDR


print("temp: {0}".format(mocky.get_pin_data(0,7,DHT22_1)))
print("light: {0}".format(mocky.get_pin_data(1,0,LDR))) # 10000 lux
mocky.get_room().setLightLevelLux(1.55) # 1.55 lux
print("light: {0}".format(mocky.get_pin_data(1,0,LDR)))

roomba = mocky.get_room() # get the room object from the mockArduino class
print(roomba) # print the room object - same ✔
print(room) # print the room object   - same ✔

print(roomba.getTemperature())


    
    
# board = pyfirmata.ArduinoDue('COM3')
# dht_pin = 2
# # set the pinmode for pin 7 to dht
# board.get_pin('d:{}:{}'.format(dht_pin, pyfirmata.DHT))
