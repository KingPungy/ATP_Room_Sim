# used in the decorator syntax
from functools import wraps
import logging
import time
import sys

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

    def __init__(self, SIMroom: Room = None, graphLength: int = 10):
        super(SIMgui, self).__init__()
        uic.loadUi("gui.ui", self)
        self.setWindowTitle("Simulation Gui")

        # if no room is passed in, create a new ones
        if SIMroom is None:
            self.room = Room()
        else:
            self.room = SIMroom

        # Default values for the gui
        self.pollRate = 1.0             # default poll rate
        self.target_temperature = 20    # default target temperature
        self.threshold = 0.5            # threshold for temperature 
        
        # set the default poll rate in the gui {Float}
        self.SensorPollRateBox.setValue(self.pollRate)
        # set the default target temperature in the gui {Int}
        self.TargetTempSelectBox.setValue(int(self.target_temperature))
        self.RoomTempSelectBox.setValue(int(self.room.getTemperature()))
        # set the default threshold in the gui {Float}
        self.TargetThreshSelectBox.setValue(self.threshold)
        self.OutTempSelectBox.setValue(int(self.room.getOutsideTemperature()))
        self.HeaterWattSelectBox.setValue(int(self.room.getHeaterPower()))
        self.CoolerBTUSelectBox.setValue(int(self.room.getCoolerPower()))

        # create a subject stream for the temperature
        self.temperature_subject = rx.subject.Subject()
        self.observablePoll = None

        # graph length for deque of values
        self.temperatureValues = deque(maxlen=graphLength)
        self.humidityValues = deque(maxlen=graphLength)

        # canvas setup for temperature and humidity graphs
        # And build graphs after canvas is added to layout
        self.TempCanvas = FigureCanvas(Figure(figsize=(3, 3), layout='tight'))
        self.verticalLayout.addWidget(self.TempCanvas)
        self.temp_ax = self.TempCanvas.figure.subplots()
        self.temp_ax.set_xlim(0, self.temperatureValues.maxlen)

        self.HumidCanvas = FigureCanvas(Figure(figsize=(3, 3), layout='tight'))
        self.verticalLayout_2.addWidget(self.HumidCanvas)
        self.humid_ax = self.HumidCanvas.figure.subplots()
        self.humid_ax.set_xlim(0, self.humidityValues.maxlen)

        # set up the buttons and spin boxes for the gui
        self.PollRateConfirm.clicked.connect(lambda: self.setPollRate(self.SensorPollRateBox.value()))
        self.TargetThreshConfirm.clicked.connect(lambda: self.setThreshold(self.TargetThreshSelectBox.value()))
        self.TargetTempConfirm.clicked.connect(lambda: self.setTargetTemperature(self.TargetTempSelectBox.value()))

        self.RoomTempConfirm.clicked.connect(lambda: self.room.setTemperature(self.RoomTempSelectBox.value()))
        self.OutTempConfirm.clicked.connect(lambda: self.room.setOutsideTemperature(self.OutTempSelectBox.value()))
        self.HeaterWattConfirm.clicked.connect(lambda: self.room.setHeaterPower(self.HeaterWattSelectBox.value()))
        self.CoolerBTUConfirm.clicked.connect(lambda: self.room.setCoolerPower(self.CoolerBTUSelectBox.value()))

        # set the state of the heater and cooler checkboxes
        self.HeaterStateBox.setChecked(self.room.isHeaterActive())
        self.CoolerStateBox.setChecked(self.room.isCoolerActive())


        # generate commands based on the measured temperature and execute them
        self.temperature_subject.pipe(
            # OPTIONAL in current version without real Hardware: convert raw sensor data to celcius
            # # ops.map(lambda RawTempData: self.ConvertRawTempDataToCelcius(RawTempData)), 
            # Functie wordt meegegeven als argument om de commands te genereren op basis van de temperatuur
            ops.map(lambda temp: self.generateCommands(temp)), 
            ops.map(lambda commands: self.executeCommands(heaterCommand=commands[0], coolerCommand=commands[1]))
            ).subscribe() 
        
        # update the plots when the temperature is updated
        # Temperature is simulated, humidity is not so it stays at 50%
        self.temperature_subject.subscribe(on_next=lambda temp: self.updatePlots(temp, self.room.getHumidity()))  

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

    def setThreshold(self, threshold: float) -> None:
        """Set the threshold for the given instance. 
        
        Args:
            threshold (float): The new threshold to be set for the instance.
        
        Returns:
            None: The function does not return any value.
        """
        if threshold <= 0:
            self.TargetThreshSelectBox.setValue(self.threshold)
            Exception("Threshold must be greater than 0, setting to 1, try again")
            print("Threshold must be greater than 0, setting to 1, try again") # for user
        else:
            self.threshold = threshold
            print(f"Threshold set to: {str(self.threshold)}")
       
    def generateCommands(self, temp: float) -> list[bool]:
        """Generates commands based on the temperature and outside temperature

        Arguments: temp {float} -- The current temperature of the room

        Returns: tuple -- Commands for the heater and cooler

        """
        
        heater_state = self.room.isHeaterActive()
        cooler_state = self.room.isCoolerActive()
        outside_temp = self.room.getOutsideTemperature()

        OutStates = [False, False]
        
        if temp < self.target_temperature - self.threshold and outside_temp < temp:
            OutStates = [True, False]
            return OutStates
        elif temp > self.target_temperature + self.threshold and outside_temp > temp:
            OutStates = [False, True]
            return OutStates
        elif temp >= self.target_temperature - (self.threshold / 2) and heater_state:
            OutStates[0] = False
            return OutStates
        elif temp <= self.target_temperature + (self.threshold / 2) and cooler_state:
            OutStates[1] = False
            return OutStates
        # elif heater_state or cooler_state:
        #     OutStates = [False, False]
        return [heater_state, cooler_state]
    
    def executeCommands(self, heaterCommand: bool, coolerCommand: bool) -> None:
        """Executes the commands for the heater and cooler

        Arguments:
            heaterCommand {bool} -- The command for the heater
            coolerCommand {bool} -- The command for the cooler

        Returns: None

        """
        self.room.activateHeater(heaterCommand)
        self.room.activateCooler(coolerCommand)
        # sets the state of the checkboxes in the GUI
        self.HeaterStateBox.setChecked(heaterCommand)
        self.CoolerStateBox.setChecked(coolerCommand)

    def updatePlots(self, temp: float | int, humid: float | int) -> None:
        """Updates the plots with the new temperature and humidity values

        Arguments:  temp {float} -- The current temperature of the room
                    humid {float} -- The current humidity of the room

        Returns: None

        """
        # print("Temp: " + str(temp) + " Humid: " + str(humid))
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
            # ops.map(lambda i: next(self.room.get_temperature())), #only used with python generator from room.py
            ops.map(lambda temperature: self.temperature_subject.on_next(self.room.getTemperature()))
        ).subscribe()
        print("Observer Created/Updated")
  
    def purgeGraphData(self) -> None:
        """Purges the graph data by clearing the deque 

        Arguments: None

        Returns: None
        """
        self.temperatureValues.clear()
        self.humidityValues.clear()


