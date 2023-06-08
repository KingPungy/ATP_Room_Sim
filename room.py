# Deprecated: This file is no longer used. It has been replaced by the C++ version in the pybind11 module.

import time
import numpy as np
import reactivex as rx

# TODO: implement in C++ for performance and use pybind11 to interface with python

class Room:
    """ A class representing a room with a temperature and humidity sensor and a heater and cooler
    
    Attributes
    ----------
    `temperature` : float
        The current temperature of the room in degrees Celsius
    `humidity` : float
        The current humidity of the room in percent
    `heater_active` : bool
        Whether the heater is currently active
    `cooler_active` : bool
        Whether the cooler is currently active
    `heater_power` : float
        The power of the heater in watts
    `cooler_power` : float
        The power of the cooler in watts
    `room_volume` : float
        The volume of the room in cubic meters
    `surface_area` : float    
        The surface area of the room in square meters
    `air_density` : float 
        The density of air in kg/m^3
    `specific_heat` : float
        The specific heat of air in J/(kg*K)
    `last_update_time` : float
        The time of the last update in seconds since the epoch
    
    Methods
    ------- 
    `get_temperature()` : float
        Returns the current temperature of the room in degrees Celsius
    `get_humidity()` : float
        Returns the current humidity of the room in percent
    `set_temperature(temperature)` : None
        Sets the current temperature of the room in degrees Celsius
    `set_humidity(humidity)` : None
        Sets the current humidity of the room in percent
    `activate_heater(is_active)` : None
        Activates or deactivates the heater
    `activate_cooler(is_active)` : None
        Activates or deactivates the cooler
    `get_heater_state()` : bool
        Returns whether the heater is currently active
    `get_cooler_state()` : bool
        Returns whether the cooler is currently active
    `calculate_temp_delta(delta_time)` : float
        Calculates the change in temperature based on heater and cooler activity
    `calculate_heat_exchange()` : float
        Calculates the heat exchange between the room and the outside based on the surface area and temperature difference

    
    
    
    """
    def __init__(self, temperature=25.0, outside_temperature=30, humidity=50.0, room_dimensions=[10, 10, 2]):
        self.temperature = temperature
        self.humidity = humidity
        
        self.accuracy_offset = np.random.uniform(-0.5,0.5) # TODO: implement accuracy offset
        
        self.outside_temperature = outside_temperature  # Initial outside temperature
        
        self.room_volume = np.prod(room_dimensions) # [w, l, h] meters
        
        self.surface_area = 2 * (room_dimensions[0] * room_dimensions[2] + room_dimensions[1] * room_dimensions[2]) # 2 x (w*h + l*h) meters^2
        self.air_density = 1.225 # kg/m^3
        self.specific_heat = 700.0 # J/(kg*K) Air heat capacity at Cv (constant volume)
        self.last_update_time = time.time()
        
        self.heater_active = False
        self.cooler_active = False
        self.heater_power = 1000.0 # watts
        self.cooler_power = 2000.0 # watts 1W is equal to 3.41 BTU/hour [W = BTU/hr / 3.41] or [BTU/hr = W × 3.41]

    def __repr__ (self):
        """Returns a string representation of the room"""
        return f"Room(\n\ttemperature={self.temperature}, \n\ttemperature_outside={self.outside_temperature}, \n\thumidity={self.humidity}, \n\theater_active={self.heater_active}, \n\tcooler_active={self.cooler_active}, \n\theater_power={self.heater_power}, \n\tcooler_power={self.cooler_power}, \n\troom_volume={self.room_volume}, \n\tsurface_area={self.surface_area}, \n\tair_density={self.air_density}, \n\tspecific_heat={self.specific_heat})"


    def get_temperature(self):
        """A generator that returns the current temperature of the room in degrees Celsius and updates the temperature based on heater and cooler activity"""
        while True:
            # Simulate time passing
            current_time = time.time()
            delta_time = current_time - self.last_update_time
            self.last_update_time = current_time

           
            self.temperature += self.calculate_temp_delta(delta_time)
            
            # Ensure temperature stays within a valid range
            clamp = lambda n, minn, maxn: max(min(maxn, n), minn)
            self.temperature = clamp(self.temperature, 0.0, 100.0)
            yield self.temperature
            # time.sleep(1)
             
    def get_humidity(self) -> float:
        return self.humidity

    def set_temperature(self, temperature) -> None:
        self.temperature = temperature

    def set_humidity(self, humidity) -> None:
        self.humidity = humidity
        
    def set_outside_temperature(self, temperature_outside):
        self.outside_temperature = temperature_outside
    
    def get_outside_temperature(self) -> float:
        return self.outside_temperature
        
    def set_heater_power(self, heater_power):
        self.heater_power = heater_power
        
    def set_cooler_power(self, cooler_power):
        self.cooler_power = cooler_power

    def activate_heater(self, is_active: bool):
        self.heater_active = is_active

    def activate_cooler(self, is_active: bool):
        self.cooler_active = is_active
    
    def get_heater_state(self) -> bool:
        return self.heater_active
    
    def get_cooler_state(self) -> bool:
        return self.cooler_active


    def calculate_temp_delta(self, delta_time) -> float:
        """Calculates the change in temperature based on heater and cooler activity
        
        Arguments: 
        `delta_time` -- the time since the last update in seconds
        
        Returns: float -- the change in temperature in degrees Celsius
        
        """	
        # Calculate the change in temperature based on heater and cooler activity
        # ΔTemp = (Δtime × Ẇatt)/(c × mass) without loss of heat 1C = 1K and changes at the same rate every time, when not taking humidity's effect of 3% faster heating at 100% humidity into account
        
        # Calculate the change in temperature based on heater and cooler activity and heat exchange with the outside
        internal_temp_change = (delta_time * ((self.heater_active * self.heater_power) - (self.cooler_active * self.cooler_power))) / (
                self.room_volume * self.air_density * self.specific_heat)

        # change the calculation below to lose heat to the outside
        external_temp_change = self.calculate_heat_exchange() * delta_time / (self.room_volume * self.air_density * self.specific_heat)

        delta_temp = internal_temp_change + external_temp_change

        return delta_temp

    def calculate_heat_exchange(self) -> float:
        """ Calculates the heat exchange between the room and the outside based on the surface area and temperature difference
        
        Arguments: None
        
        returns: float -- the heat exchange in watts, positive if heat is gained from the outside, negative if heat is lost to the outside
        
        """ 
        # Calculate the heat exchange between the room and the outside based on the surface area and temperature difference
        thermal_conductivity_brick = 0.18  # Thermal conductivity of insulatedbrick (W/m*K)
        thickness_brick = 0.3  # Thickness of brick wall (m)
        temperature_diff = self.temperature - self.outside_temperature

        # Qw = As*Uc*ΔTemp heat loss via walls heat loss via conduction through brick wall
        heat_exchange = (self.surface_area * thermal_conductivity_brick * temperature_diff) / thickness_brick
        
        # print(f"heat_exchange: {heat_exchange}")
        return -heat_exchange # in watts


        
    