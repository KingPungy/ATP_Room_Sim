# used in the decorator syntax
from functools import wraps
import math
import numpy as np
import logging
import time
import sys

from typing import Union
from collections import deque # for deque of temperature values
# for plotting in qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure  # for plotting in qt

from PyQt5 import QtCore, QtWidgets  # for gui widgets you might want to add
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget  # for gui window and app
from PyQt5 import uic  # for loading ui files

import reactivex as rx
# from reactivex import scheduler
from reactivex import operators as ops
from room_simulator import Room # New room class and temperature generator
from MockFirmata import MockFirmata # mock arduino class

from constants import * # pin definitions


class SIMgui(QMainWindow):
    """A class representing the gui for the simulation and the logic for the simulation

    Attributes
    ----------
    `room` : Room
        The room object that the simulation is based on
    `pollRate` : float
        The rate at which the temperature is polled in seconds
    `target_temperature` : float
        The target temperature of the room in degrees Celsius
    `temperature_subject` : rx.subject.Subject
        The subject stream for the temperature
    `observablePoll` : rx.disposable.Disposable 
        The disposable object for the observer
    `temperatureValues` : collections.deque
        The deque of temperature values for the graph
    `humidityValues` : collections.deque
        The deque of humidity values for the graph
    `temp_ax` : matplotlib.axes.Axes
        The axes for the temperature graph
    `humid_ax` : matplotlib.axes.Axes
        The axes for the humidity graph
    `TempCanvas` : matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg
        The canvas for the temperature graph
    `HumidCanvas` : matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg
        The canvas for the humidity graph
    `verticalLayout` : PyQt5.QtWidgets.QVBoxLayout
        The vertical layout for the temperature graph
    `verticalLayout_2` : PyQt5.QtWidgets.QVBoxLayout
        The vertical layout for the humidity graph
    `SensorPollRateBox` : PyQt5.QtWidgets.QDoubleSpinBox
        The spin box for the poll rate
    `RoomTempSelectBox` : PyQt5.QtWidgets.QDoubleSpinBox
        The spin box for the room temperature
    `TargetTempSelectBox` : PyQt5.QtWidgets.QDoubleSpinBox
        The spin box for the target temperature
    `OutTempSelectBox` : PyQt5.QtWidgets.QDoubleSpinBox
        The spin box for the outside temperature
    `HeaterWattSelectBox` : PyQt5.QtWidgets.QDoubleSpinBox
        The spin box for the heater power
    `CoolerBTUSelectBox` : PyQt5.QtWidgets.QDoubleSpinBox
        The spin box for the cooler power
    `PollRateConfirm` : PyQt5.QtWidgets.QPushButton
        The button for confirming the poll rate
    `RoomTempConfirm` : PyQt5.QtWidgets.QPushButton
        The button for confirming the room temperature
    `TargetTempConfirm` : PyQt5.QtWidgets.QPushButton
        The button for confirming the target temperature
    `OutTempConfirm` : PyQt5.QtWidgets.QPushButton
        The button for confirming the outside temperature
    `HeaterWattConfirm` : PyQt5.QtWidgets.QPushButton
        The button for confirming the heater power
    `CoolerBTUConfirm` : PyQt5.QtWidgets.QPushButton
        The button for confirming the cooler power

    Methods
    -------
    `setTargetTemperature(target_temperature)` : None
        Sets the `target_temperature`
    `setThreshold(threshold)` : None
        Sets the `threshold`
    'generateCommands(temp)` : None
        Generates commands based on the temperature and outside temperature
    `ExecuteCommands(temp)` : None
        Executes commands based on the temperature and outside temperature
    `updatePlots(temp,humid)` : None
        Updates the plots with the new temperature and humidity values
    `updateObserver()` : None
        Updates the observer with the current poll rate
    `setPollRate(nPollRate)` : None
        Sets the poll rate of the observer and updates the observer
    `purgeGraphData()` : None
        Purges the graph data by clearing the deque

    """

    def __del__(self):
        
        print("Disposed of Observer and subscribers")
        self.observablePoll.dispose()
        self.temperature_subject.dispose()

    def __init__(self, MockFirmata: MockFirmata = None, graphLength: int = 10):
        super(SIMgui, self).__init__()
        uic.loadUi("gui.ui", self)
        self.setWindowTitle("Simulation Gui")

        # if no room is passed in, create a new ones
        if MockFirmata is None:
            raise Exception("MockFirmata object not passed in")
        

        self.room = MockFirmata.getRoomObject() # get the room object from the MockFirmata object to alter values in the simulation
        self.firmata = MockFirmata # get the MockFirmata object to Read and Write to the MockArduino


        # Default values for the gui
        self.pollRate = 1.0             # default poll rate
        self.target_temperature = 20    # default target temperature
        self.temp_threshold = 0.5            # threshold for temperature 

        self.lux_threshold = 10000     # threshold for light level  
        
        # set the default poll rate in the gui {Float}
        self.SensorPollRateBox.setValue(self.pollRate)
        self.ActiveTempControlCheckBox.setChecked(False) #self.ActiveTempControlCheckBox.isChecked())
        # self.ActiveTempControlCheckBox.clicked.connect(lambda: print("clicked")) #self.ActiveTempControlCheckBox.isChecked())
        
        
        # set the default target temperature in the gui {Int}
        self.TargetTempSelectBox.setValue(int(self.target_temperature))
        self.RoomTempSelectBox.setValue(int(self.room.getTemperature()))
        # set the default threshold in the gui {Float}
        self.TargetThreshSelectBox.setValue(self.temp_threshold)
        self.OutTempSelectBox.setValue(int(self.room.getOutsideTemperature()))
        self.HeaterWattSelectBox.setValue(int(self.room.getHeaterPower()))
        self.CoolerBTUSelectBox.setValue(int(self.room.getCoolerPower()))

        # create a subject stream for the temperature
        self.temperature_light_subject = rx.subject.Subject()
        self.observablePoll = None

        # graph length for deque of values
        self.temperatureValues = deque(maxlen=graphLength)
        self.humidityValues = deque(maxlen=graphLength)

        # canvas setup for temperature and humidity graphs
        # And build graphs after canvas is added to layout
        self.TempCanvas = FigureCanvas(Figure(figsize=(3, 3), layout='tight'))
        self.TempGraphLayout.addWidget(self.TempCanvas)
        self.temp_ax = self.TempCanvas.figure.subplots()
        self.temp_ax.set_xlim(0, self.temperatureValues.maxlen)

        self.HumidCanvas = FigureCanvas(Figure(figsize=(3, 3), layout='tight'))
        self.HumidGraphLayout.addWidget(self.HumidCanvas)
        self.humid_ax = self.HumidCanvas.figure.subplots()
        self.humid_ax.set_xlim(0, self.humidityValues.maxlen)

        # set up the buttons and spin boxes for the gui
        self.PollRateConfirm.clicked.connect(lambda: self.setPollRate(self.SensorPollRateBox.value()))
        self.TargetThreshConfirm.clicked.connect(lambda: self.setTempThreshold(self.TargetThreshSelectBox.value()))
        self.TargetTempConfirm.clicked.connect(lambda: self.setTargetTemperature(self.TargetTempSelectBox.value()))
        
        # lux slider and threshold
        self.OutsideLuxSlider.valueChanged.connect(lambda: self.room.setLightLevelLux(self.OutsideLuxSlider.value()))
        self.OutsideLuxSlider.valueChanged.connect(lambda: print("SLIDING: ", self.room.getLightLevelLux()))
        self.LuxThreshConfirm.clicked.connect(lambda: self.setLuxThreshold(self.LuxThreshSelectBox.value()))


        self.RoomTempConfirm.clicked.connect(lambda: self.room.setTemperature(self.RoomTempSelectBox.value()))
        self.OutTempConfirm.clicked.connect(lambda: self.room.setOutsideTemperature(self.OutTempSelectBox.value()))
        self.HeaterWattConfirm.clicked.connect(lambda: self.room.setHeaterPower(self.HeaterWattSelectBox.value()))
        self.CoolerBTUConfirm.clicked.connect(lambda: self.room.setCoolerPower(self.CoolerBTUSelectBox.value()))

        # set the state of the heater and cooler checkboxes
        self.HeaterStateBox.setChecked(self.room.isHeaterActive())
        self.CoolerStateBox.setChecked(self.room.isCoolerActive())
        self.SunscreenStateBox.setChecked(self.room.isSunscreenActive())


        # generate commands based on the measured temperature and execute them
        # add inside temp, outside temp and light level as pipe inputs to the subject stream
        self.temperature_light_subject.pipe(
            # OPTIONAL in current version without real Hardware: convert raw sensor data to celcius
            # # ops.map(lambda RawData: self.ConvertRawDataToCelciusAndLux(RawData[0], RawData[1], RawData[2])), 
            # Functie wordt meegegeven als argument om de commands te genereren op basis van de temperatuur
            # data object is als volgt opgebouwd: [[inside_temp, inside_humid], [outside_temp, outside_humid], light_level_lux]
            ops.map(lambda data: self.generateCommands(inside_temp=data[0][0], outside_temp=data[1][0], 
                                                       target_temperature=self.target_temperature, temp_threshold=self.temp_threshold,
                                                       heater_state=self.firmata.digitalRead(RELAY_HEATER), 
                                                       cooler_state=self.firmata.digitalRead(RELAY_COOLER), 
                                                       sunscreen_state=self.firmata.digitalRead(RELAY_SUNSCREEN), 
                                                       ActiveTempControlEnabled=self.ActiveTempControlCheckBox.isChecked(),
                                                       lux=data[2], lux_threshold=self.lux_threshold
                                                       )),
            ops.map(lambda commands: self.executeCommands(heaterCommand=commands[0], coolerCommand=commands[1], sunscreenCommand=commands[2]))
            ).subscribe() 
        
        # update the plots when the temperature is updated
        # Temperature is simulated, humidity is not so it stays at 50%
        self.temperature_light_subject.subscribe(on_next=lambda data: self.updatePlots(data[0][0], self.room.getHumidity()))  

        # create an observable that emits every 1/poll_rate seconds and updates the temperature_subject with the current temperature of the room
        self.updateObserver()
        # set the initial values and labels of the plots
        self.updatePlots(0, 0)
        self.purgeGraphData() 
    


    def setTargetTemperature(self, target_temperature: float) -> None:
        """Sets the `target_temperature`

        Arguments: target_temperature {float} -- The target temperature
        
        Returns: None

        """
        self.target_temperature = target_temperature
        print(f"Target Temperature set to: {str(self.target_temperature)}")
    
    def setTempThreshold(self, threshold: float) -> None:
        """Set the threshold for the given instance. 
        
        Args:
            threshold (float): The new threshold to be set for the instance.
        
        Returns:
            None: The function does not return any value.
        """
        if threshold <= 0:
            self.TargetThreshSelectBox.setValue(self.temp_threshold)
            Exception("Threshold must be greater than 0, setting to 1, try again")
            print("Threshold must be greater than 0, setting to 1, try again") # for user
        else:
            self.temp_threshold = threshold
            print(f"Threshold set to: {str(self.temp_threshold)}")
          
    def setLuxThreshold(self, lux_threshold: int) -> None:
        """Sets the `lux_threshold`

        Arguments: lux_threshold {int}: The lux threshold
        
        Returns: None

        """
        self.lux_threshold = lux_threshold
        print(f"Light Level Threshold set to: {str(self.lux_threshold)}")
    
    def calculateLuxFromADC(self,mapped_value:int) -> Union[float, int]:
        """Calculates the lux value from an ADC mapped value.

        Args:
            mapped_value {int}: The ADC mapped value.
            
        Returns:
            float or int: The lux value calculated from the given ADC mapped value.
        """
        # Constants for your LDR setup (should match the constants used in the Arduino code)
        R10lx = 15000.0  # Light resistance at 10 lux in ohms
        gamma = 0.6      # Gamma value
        R1 = 5000.0      # Resistor R1 in ohms from voltage divider
        VCC = 5.0        # Supply voltage in volts

        # Calculate voltage from mapped value
        voltage = (mapped_value / 1024.0) * VCC

        # Calculate LDR resistance LDR_R using voltage and R1
        LDR_R = R1 * (VCC - voltage) / voltage

        # get callibration values for conversion from lux to ldr resistance and back
        # def calculateLDRResistance(self, lux,  R10lx, gamma): 
        #     return (10 ** gamma) * R10lx / (lux ** gamma)
        
        # loglist = []
        # luxList = []
        # # fill a list with ldr_R values from the calculateLDRResistance function and calculate the logfit
        # for i in [1,2,10,100,1000,10000,100000]:
        #     luxList.append(i)
        #     loglist.append(calculateLDRResistance(i, R10lx, gamma))
        
        # logFit = np.polyfit(np.log(luxList), np.log(loglist), 1)
        # print(logFit) # [ -0.6 ,  10.99735654]
        # print(f"Log(R10lx) = {math.log(R10lx)}")
        
        # Calculate lux using gamma formula
        a = (math.log(LDR_R) - 11.02) / -gamma # max error% = -8.7% at 100000 lux, lower error at lower lux levels around -0.5 to 3%
        lux = math.exp(a)
        
        return lux

    


    def setPollRate(self, nPollRate: float) -> None:
        """ Sets the poll rate of the observer and updates the observer

        calls `self.UpdateObserver()` and `self.purgeGraphData()` to update the observer and purge the graph data to start fresh with the new poll rate

        Arguments: `nPollRate` {float} -- The new poll rate

        Returns: None

        """
        if nPollRate <= 0:
            self.SensorPollRateBox.setValue(self.pollRate)
            Exception("Poll Rate must be greater than 0, setting to 1, try again")
            print("Poll Rate must be greater than 0, setting to 1, try again") # for user
        else:
            self.pollRate = nPollRate
            self.purgeGraphData()
            self.updateObserver()
            print(f"Poll Rate set to: {str(self.pollRate)}/s")


    def generateCommands(self,inside_temp: float, outside_temp: float, target_temperature: float, temp_threshold: float, heater_state: bool, cooler_state: bool, sunscreen_state: bool, ActiveTempControlEnabled: bool, lux:float, lux_threshold:float) -> list[bool]:
        """Generate commands to control the heater, cooler and sunscreen based on temperature and light levels.

        Args:
            inside_temp (float): The current temperature inside the room.
            outside_temp (float): The current temperature outside the room.
            target_temperature (float): The desired temperature inside the room.
            temp_threshold (float): The acceptable range of temperatures around the target temperature.
            heater_state (bool): The current state of the heater.
            cooler_state (bool): The current state of the cooler.
            sunscreen_state (bool): The current state of the sunscreen.
            ActiveTempControlEnabled (bool): Whether active temperature control is enabled.
            lux (float): The current light level in the room.
            lux_threshold (float): The threshold at which the sunscreen should be activated.

        Returns:
            list[bool]: A list of booleans representing the new states of the heater, cooler and sunscreen.
        """ 
        OutStates = [heater_state, cooler_state, sunscreen_state] # default state of the heater and cooler and sunscreen
        # print(f"Calculated Lux level: {lux}   from : {self.firmata.analogRead(LDR)}    Room lux: {self.room.getLightLevelLux()}   Error%: {  ((lux - self.room.getLightLevelLux())/ self.room.getLightLevelLux()) * 100 }%")
        if lux > lux_threshold:
            OutStates[2] = True
        else:
            OutStates[2] = False

 
        if inside_temp < target_temperature - temp_threshold and ((outside_temp < inside_temp) or ActiveTempControlEnabled): 
            # if the temperature is below the target temperature and the outside temperature is lower than the inside temperature or the active temp control is enabled: turn on the heater
            OutStates[0] = True
            OutStates[1] = False
            return OutStates
        elif inside_temp > target_temperature + temp_threshold and ((outside_temp > inside_temp) or ActiveTempControlEnabled): 
            # if the temperature is above the target temperature and the outside temperature is higher than the inside temperature or the active temp control is enabled: turn on the cooler
            OutStates[0] = False
            OutStates[1] = True
            return OutStates
        elif inside_temp >= target_temperature - (temp_threshold / 2) and heater_state: # if the temperature is within the acceptable range and the heater is on: turn it off
            OutStates[0] = False
            return OutStates
        elif inside_temp <= target_temperature + (temp_threshold / 2) and cooler_state: # if the temperature is within the acceptable range and the cooler is on: turn it off
            OutStates[1] = False
            return OutStates
        
        return OutStates

    def executeCommands(self, heaterCommand: bool, coolerCommand: bool, sunscreenCommand: bool) -> None:
        """This function sets the state of the checkboxes in the GUI and writes the given commands to the firmata.
        
        Args:
            heaterCommand (bool): The state of the heater.
            coolerCommand (bool): The state of the cooler.
            sunscreenCommand (bool): The state of the sunscreen.
        
        Returns:
            None
        """
        self.firmata.digitalWrite(RELAY_HEATER, heaterCommand)
        self.firmata.digitalWrite(RELAY_COOLER, coolerCommand)
        self.firmata.digitalWrite(RELAY_SUNSCREEN, sunscreenCommand)
        
        # sets the state of the checkboxes in the GUI
        self.HeaterStateBox.setChecked(heaterCommand)
        self.CoolerStateBox.setChecked(coolerCommand)
        self.SunscreenStateBox.setChecked(sunscreenCommand)


    def updatePlots(self, temp: Union[float, int], humid: Union[float, int]) -> None:
        """Updates the plots with the new temperature and humidity values

        Arguments:  temp {float} -- The current temperature of the room
                    humid {float} -- The current humidity of the room

        Returns: None

        """
        # add the new values to the deque
        self.temperatureValues.append(temp)
        self.humidityValues.append(humid)

        # clear the axes
        self.temp_ax.cla()
        self.humid_ax.cla()

        # set labels and titles
        self.temp_ax.set_ylabel("Temperature °C")
        self.temp_ax.set_title("Temperature")
        self.humid_ax.set_ylabel("Humidity %")
        self.humid_ax.set_title("Humidity")
        # sets the grid
        self.temp_ax.grid()
        self.humid_ax.grid()

        # limits the y axis to the min and max values of the data +- 3
        self.temp_ax.set_ylim(min(self.temperatureValues)-3,
                              max(self.temperatureValues)+3)
        self.humid_ax.set_ylim(min(self.humidityValues)-3,
                               max(self.humidityValues)+3)

        # Set axis limit to the length of the deque so it shows towards the right of the graph
        self.temp_ax.set_xlim(len(self.temperatureValues) -
                              self.temperatureValues.maxlen, len(self.temperatureValues))
        self.humid_ax.set_xlim(
            len(self.humidityValues)-self.humidityValues.maxlen, len(self.humidityValues))

        # # set the x axis to the length of the deque
        # self.temp_ax.set_xlim(0,self.temperatureValues.maxlen)
        # self.humid_ax.set_xlim(0,self.humidityValues.maxlen)

        # color the lines
        self.temp_ax.plot(self.temperatureValues, 'r')
        self.humid_ax.plot(self.humidityValues, 'b')
        self.TempCanvas.draw()
        self.HumidCanvas.draw()
        # plt.pause(0.001)

    def purgeGraphData(self) -> None:
        """Purges the graph data by clearing the deque 

        Arguments: None

        Returns: None
        """
        self.temperatureValues.clear()
        self.humidityValues.clear()

    def updateObserver(self) -> None:
        """Updates the observer with the current poll rate

            `self.observablePoll` is disposed of and a new one is created with the new poll rate

        Arguments: None

        Returns: None

        """
        # optimal_thread_count = multiprocessing.cpu_count()
        # pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

        if self.observablePoll != None:
            self.observablePoll.dispose() if self.observablePoll != None else None

        self.observablePoll = rx.interval(1.0/self.pollRate).pipe(
            ops.map(lambda Data : self.temperature_light_subject.on_next(
                [self.firmata.digitalRead(DHT22_1), self.firmata.digitalRead(DHT22_2), self.calculateLuxFromADC(self.firmata.analogRead(LDR))]
                ))
        ).subscribe()
        print("Observer Created/Updated")
  



# if False == True:
    # print("Starting Simulation Gui Test")

    # app = QApplication(sys.argv)

    # sim = SIMgui(Room(),10)
    # sim.show()
    # print(sim.room.getLightLevelLux())
    # print(sim.calculateLuxFromADC(977))

    # app.exec_()

