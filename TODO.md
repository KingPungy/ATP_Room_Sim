
### TODO


#### Code:

- MockFirmata && mockDuino classes
    - getPin("analog/Digital","pin number", data format) 
    - MockFirmata.Board("Type:Due,Uno","COM PORT")
    - SetPin("DHT,Analog")

- RoomSim class
    - add Light level and LDR Sensor from MockDuino
    - add get and set for light level

- SimGUi controller classes
    - Add Graph for Light value to UI
    - Add Outside light level slider in Lux to UI
    - ToLux("value", "Resistor", Constant?)
    - GenerateSunscreenCommand("lux", "luxThreshold")

functionele test maken
door lijsts met input, output pairs mee te geven en te asserten


#### Vragen:

- write I2C communicatie naar de Sensoren toe.
-   return van de sensor mag random en simpel zijn.
-   firmata is niet de bedoeling
-   uitvogelen hoe i2c werkt voor de sensor

-? actuatoren aansturen moet ook ingewikkeld. ???
-? how to mock i2c? in either C++ or Python?
    -? de output van de getTemperature() functie als i2C data encoden?
    - onderzoeken op welke manier pyFirmata sensor waardes terug geeft van de sensoren. 
    - vervang deze functies als de hardware aanwezig is. Check voor pyfirmata board connection 
    - simuleer de pyfirmata functies in c++, alleen degene die nodig zijn.

    # - make a class called MockFirmata inside the c++ module that mocks the use of the same functions. 


- in het testplan beschijven wat en hoe je het functioneel programeren gaat toepassen.
-? Is wat ik nu heb voldoende voor functioneel programmeer eisen?
    - map    ✔?
    - reduce X onnodig voor huidige implementatie
    - fold   X onnodig voor huidige implementatie
    - zip    X onnodig voor huidige implementatie
-✔ welke andere sensor toevoegen ?
    ✔ licht sensor / zonnescherm motor, mogelijk timer om tijd die de moter erover doet te mocken
        - zonnestand / lumen / lux / via UI zon sterkte invullen
    - lucht druk / ramen openen of zien of ramen open zijn om niet te verwarmen
    X co2/luchtkwaliteit / ramen openen 

## Parts

Sensoren
- light
    - GL5528 LDR, Buiten
        - Analog pin
        - requires logarithmic formula to convert to Lux
            - this is not neccesarily needed for threshold control
        - operating temps
        - limits

- Temp
    - DHT22 x2, Binnen Buiten
        - Digital pins,
        - pulse width decoding
            - library inside pyfirmata gives nessecary outputs, takes 2 seconds
            - just simulate the returned values and the connection to the board.


classes:
- UI Py
- sensor reading class Py
- MockFirmata Py
- MockArduino + SimRoom C++
- 




### Requirements testplan:
- describe function of the system, (redenering)
- Describe what data is collected by the sensors and why and how they are used.
- describe the physical plan and reasons for used protocols and libraries if it were to be build, pyFirmata on arduino and python.
- what is the system supposed to do and under what conditions, weather, speed?, 

- describe the sensors and how they fulfill physical requirements and can operate under the proposed conditions
- describe Actuators used and why they are used and for what purpose

- Describe risks, and why which tests are writen and which aren't for simplicity
- describe criteria and how i plan to abide by those using tests
- describe a few tests and methods 

- simple class diagram, (plant uml)
- hardware diagram, (drawIO) of (online arduino sim builder) of (fritzing)
- flowchart without code inside
- 
- Describe decorator use NOT working
    - Exploratory testing
    - Why is the decorator usefull and what type are you adding
    - function time logging, function output logging
    - WHY is this usefull


inleiding
hardware
software
testen


#### tests:
- inputs geven, outputs testen
- runt de software?
- toestand meten ofm loop van het programma te testen
- orakel testen, 2+2 = 4 kan ik testen als orakel,  algemene snelheid van een beladen afrikaanse vogel of de verwachte verandering in temperatuur. dit moet je ergens anderes vandaan halen of berekenen.
#### types:

- box testing
    blackbox - geen kennis van de interne werking, dus test de uitkomst. door iemand die misschien niet weet wat het doet en allen gewoon maar probeerd
    whitebox - wel kennis van de interne werking en test dus ook de interne werkingen. door  de programmeurs zelf en weet dus waar dingen mogelijk fout kan gaan. of iemand anders die weet waar het aan moet voldoen.

- smoke testing, gaat het kapot als ik het gewoon gebruik. compilen, runnen
- exploratory testing: kennen van de code, kijken naar de code, waar verwacht ik fouten voor te komen

#### soort tests, test niveaus:
- unit - single function or line of code in a function , test inputs, ints, floats, doubles, vectors, BSN nummer??
- subsystem testing - single part of the code, test library, test every function inside library as unit test and the whole is a subsystem test
- system integration - single feature output mostly blackbox testing by checking the wanted change in the system, READ THE READER
- regression - NOT USED IN PROJECT, verbeteringen/veranderingen testen
- acceptance - NOT USED IN PROJECT, door klant uitgevoerd, kijken of het aan alle eisen voldoet

#### Risk based testing
- master testplan
    - tijd is kostbaar
    - waar alloceer je tests
    - voorkom overlap

- risk = chance of failure x Damage
- notification led test, high failure chance, low damage
- car brakes, low failure chance, high damage when bugs are present,
- high damage risk are the important ones
- wat voor gevaar levert het risico van het niet testen van een element op, tijd voor reparatie kan ook risico zijn

#### Strategie
- 100% niet mogelijk
- welke risico's als iets niet getest wordt
- waarom test je bepaalde dingen niet en zijn de risocos minimaal
- waar komen de kwaliteitscriteria vandaan. ISO 25010
- bepaal benodigde infrastuructuur.
- onderhoudbaarheid, correctheid, 
- hangen aan niveus, correctheid = unit test, 

- bekijk de powerpoint voor strategie test niveau