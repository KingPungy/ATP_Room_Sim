# This file contains the class that mocks the Arduino Firmata library for testing purposes
import room_simulator as rs
from room_simulator import Room
import time


# pin modes
# EMPTY = 0 # will produce error if data is requested from analog pin with empty pinmode

# digital only
# DHT22_1 = 1
# DHT22_2 = 2
# RELAY_HEATER = 3
# RELAY_COOLER = 4
# RELAY_SUNSCREEN = 5

# analog only
# LDR = 6



class MockFirmata:
    def __init__(self,Port= 3, Room = Room) -> None:
        self.port = Port
        self.MockArduino = rs.mockArduino(3, Room) # COM3 port and room object
        self.Connected = False
        self.pinTypes = { "d": 0, "a": 1 }
        self.pinModes = { "EMPTY": 0, "DHT22_1": 1, "DHT22_2": 2, "RELAY_HEATER": 3, "RELAY_COOLER": 4, "RELAY_SUNSCREEN": 5, "LDR": 6 }

    def begin(self) -> bool:
        """
        Checks if MockArduino is connected to specified port and returns a boolean value. 
        
        Args:
            self: an instance of the object

        Returns:
            A boolean value indicating whether the connection was successful or not.
        """
        if self.MockArduino.get_com_Port() == self.port:
            print("MockArduino connected to port: {0}".format(self.port))
            self.Connected = True
            return True
        else:
            raise Exception("MockArduino not connected to port")

    def getRoomObject(self) -> Room:
        """
        Returns the room object from the MockArduino class.
        
        Args:
            self: an instance of the object

        Returns:
            The room object from the MockArduino class.
        """
        return self.MockArduino.get_room()
    # This function sets the pin mode for a given pin on the MockArduino object
    def setPinMode(self, pinDef:str) -> None:
        """Sets the pin mode for a given pin on the MockArduino object.
        Args:
            pinDef (str): A string in the format '(d)igital/(a)nalog:pinNum:pinMode'
        Returns:
            None
        """
        # Split string like "d:7:DHT22_1" into list ["d","7","DHT22_1"]	
        pinDef = pinDef.split(":")
        
        # Check if pinDef is in correct format
        if len(pinDef) != 3:
            raise Exception("pinDef not in correct format, ecpected '(d)igital/(a)nalog:pinNum:pinMode'")
                
        else:
            # Check if pinType is in correct format
            if pinDef[0] in "da":
                pinType = self.pinTypes[pinDef[0]]
            else:
                raise Exception("pinType not in correct format")
                    
            # Convert pin number from string to int
            pinNum = int(pinDef[1]) # MockArduino handles exceptions
            
            #check if pinmode exists
            if pinDef[2] not in self.pinModes:
                raise Exception("pinMode not in correct format, check pinModes in MockFirmata.py")    
            else:
                pinMode = self.pinModes[pinDef[2]]
            
            # Set pin mode in MockArduino object
            self.MockArduino.set_pin_mode(pinType,pinNum,pinMode)
    
    def digitalWrite(self, pin:int, value:bool) -> None:
        """Set the digital pin of an Arduino. 
        
        Args: 
            pin (int): The pin number to set. 
            value (bool): The value to set the pin to. 
        
        Returns: 
            None. 
        """
        self.MockArduino.set_digital_pin(pin, value)
            
    def digitalRead(self, pin:int) -> [bool,[float,float]]:
        """
        Reads the digital value of a specified pin on an Arduino board.
        
        Args: 
            pin (int): The pin number to read from.
        
        Returns:
            bool: The digital value of the pin. given a pin that has a pinmode of 0 or a relay pinmode
            [float,float]: A list containing the temperature and humidity on a DHT Pin.
        """
        return self.MockArduino.get_pin_data(0,pin)
        
    def analogRead(self, pin:int) -> float:
        """ 
        Reads the analog value from a given pin on the Arduino.
        
        Args:
            pin: The pin number of the Arduino to read from
        
        Returns:
            A float value representing the analog reading from the pin 
        """
        return self.MockArduino.get_pin_data(1,pin)


# Testing
# ===========================================================

room = rs.Room(temperature=25.0, outside_temperature=30,
                   humidity=20.0, room_dimensions=[10, 10, 2]) # breedte, lengte, hoogte


if True:

    mocky = MockFirmata(3, room)
    mocky.begin()

    mocky.setPinMode("d:7:DHT22_1") # pin D7 is DHT22_1
    mocky.setPinMode("d:8:DHT22_2") # pin D8 is DHT22_2

    mocky.setPinMode("d:30:RELAY_HEATER") # pin D9 is RELAY_HEATER
    mocky.setPinMode("d:32:RELAY_COOLER") # pin D10 is RELAY_COOLER
    mocky.setPinMode("d:34:RELAY_SUNSCREEN") # pin D11 is RELAY_SUNSCREEN

    mocky.setPinMode("a:0:LDR") # pin A0 is LDR
    # format the return value below into tempo and humidity
    print(mocky.digitalRead(7))

    #  testing minimum read interval of DHT sensors
    result = mocky.digitalRead(7)
    print(f"Temp: {result[0]} °C, Humidity: {result[1]} %") # 25.0, 20.0

    result = mocky.digitalRead(7)
    print(f"Temp: {result[0]} °C, Humidity: {result[1]} %") # 25.0, 20.0

    result = mocky.digitalRead(7)
    print(f"Temp: {result[0]} °C, Humidity: {result[1]} %") # 25.0, 20.0

    time.sleep(3)

    result = mocky.digitalRead(7)
    print(f"Temp: {result[0]} °C, Humidity: {result[1]} %") # 25.0, 20.0

    result = mocky.digitalRead(7)
    print(f"Temp: {result[0]} °C, Humidity: {result[1]} %") # 25.0, 20.0

    print(f"Light Level between 0-1024: {mocky.analogRead(0)}") # 10000 lux

    mocky.digitalWrite(30, True) # turn on heater
    print(f"Heater state: {mocky.digitalRead(30)}") # True


# mocky = rs.mockArduino(3, room) # COM3 port and room object
# print(mocky.get_com_Port()) # COM3


# mocky.set_pin_mode(0,7,DHT22_1) # pin D7 is DHT22_1
# mocky.set_pin_mode(1,0,LDR) # pin A0 is LDR


# print("temp: {0}".format(mocky.get_pin_data(0,7)))
# print("light: {0}".format(mocky.get_pin_data(1,0))) # 10000 lux
# mocky.get_room().setLightLevelLux(1.55) # 1.55 lux
# print("light: {0}".format(mocky.get_pin_data(1,0)))

# roomba = mocky.get_room() # get the room object from the mockArduino class
# print(roomba) # print the room object - same ✔
# print(room) # print the room object   - same ✔

# print(roomba.getTemperature())



    
    
# board = pyfirmata.ArduinoDue('COM3')
# dht_pin = 2
# # set the pinmode for pin 7 to dht
# board.get_pin('d:{}:{}'.format(dht_pin, pyfirmata.DHT))
