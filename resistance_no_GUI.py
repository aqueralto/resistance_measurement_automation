# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 14:32:12 2021

@author: Albert Queraltó

This is a simple script that initializes a Fuji PXR4 and a Keithley 2182 nanovoltimeter in order to
read the temperature and voltage continuously. In addition, it also reads the current input from a
Keithley 224 sourcemeter. The data is used to calculate the resistance and saved row by row in a "txt" file.
"""

#!/usr/bin/env python 
import time
import csv
import serial
import minimalmodbus
import pyvisa
import enum

# Initialization of the Fuji PXR4 device using the minimalmodbus library
fuji = minimalmodbus.Instrument(mode = 'rtu', port = 'COM3', slaveaddress = 1, # Port is hardcoded as COM3 and slaveaddress as 1
                                close_port_after_each_call = False,
                              debug = False)  # port name, slave address (in decimal)

# Setting up specific configuration parameters
fuji.serial.baudrate = 9600 # Baudrate must be the same as the instrument, otherwise it won't read anything (=9600 for the Fuji PXR4)
fuji.serial.bytesize = 8
fuji.serial.parity = serial.PARITY_NONE
fuji.serial.stopbits = 1
fuji.serial.timeout = 1 # seconds
fuji.clear_buffers_before_each_transaction = True

# Initialization of the Keithley 2182 device using the pyvisa library
rm = pyvisa.ResourceManager() # Finds all visa resources
keithley2182 = rm.open_resource('GPIB0::6::INSTR') # Selects the specific port for our device. Hardcoded as GPIB0::6::INSTR
keithley2182.write("*rst; status:preset; *cls") # Resets the device; status registers to default state; clears all events and errors
keithley2182.write(":INIT:CONT ON") # Initiates measurement cycle as continuous
keithley2182.write(':SENS:VOLT:NPLC %s' % str(1)) # Sets the reading rate for the volts in PLCs (Power Line Cycles) from 0.01 to 50/60 Hz
keithley2182.write("*WAI") # Wait until all previous commands have been executed

# Initialization of the Keithley 224 device using the pyvisa library
"""For some reason, the device is not working properly. The current is correctly set, but when operate is on, the voltage values
are different than the ones observed with manual operation. Therefore, I commented this part."""
#keithley224 = rm.open_resource('GPIB0::19::INSTR') # Selects the specific port for our device. Hardcoded as GPIB0::19::INSTR
#current = float(10e-06) # Set current value
current_reading = 100e-06 # Set current value for resistance calculation
#keithley224.write('I' + str(current) + 'X') # Write current value to instrument
#operate = True # Set operate to true

# Check whether operate is true or not
if operate is True:
   keithley224.write('F1X') # Turns output on
else:
   keithley224.write('F0X') # Turns output off

# Create empty file to write the readings
fileName = input("Enter the name of the file: ") # Ask for filename
with open(fileName, "w") as file:
    recording = csv.writer(file, delimiter = ',')
    recording.writerow(["Process time (s)", "Current (uA)", "Temperature (ºC)", "Voltage (V)", "Resistance (Ohms)"]) # Write the headers of the file
file.close() # Close the file

# Define the starting time
start = time.time()

# Loop for Data Acquisition in continuous mode
while True:
    
    ##### Reading current input from Keithley 224 #####
    # https://www.eevblog.com/forum/testgear/keithley-224-python-code/
#    readout = keithley224.read()  
#    splitted = readout.split(',')
#
#    for element in splitted:
#        if 'DCI' in element:
#            current_reading = float(element[4:])
    
    ##### Reading temperature from Fuji PXR4 #####
    
    # We will use the read_register method to record the temperature. The parameters that we will pass
    # to the method are:
    #     - The 'registeraddress' which stores different values depending on its number. To read the temperature it must be set to 0.
    #     - The 'number of decimals' indicates by how much the value in the 'registeraddress' will be divided by. Since it is stored as
    #       an integer number, we selected 1 to read the temperature correctly.
    #     - The 'function code' refers to a Modbus function, the number 4 is for the holding registers.
    
    temperature = fuji.read_register(0, 1, 4) # Registeraddress, number of decimals, function code (4 = holding registers)
    
    ##### Reading voltage from Keithley 2182 #####
    voltage = keithley2182.query(":DATA:FRESh?") # Requests the latest available reading in the device.
                                             # Can repeatedly return the same reading until there is a new reading.
                                             # This will depend on the PLC value.
    
    voltage = float(voltage)       
                                
    # Calculate the resistance
    # if/else statement to handle division by zero
    if current_reading == 0.0:
        resistance = 0
    else:
        resistance = voltage / current_reading
        
    # Print the time, current, temperature, voltage and resistance values
    print(time.time()-start, current_reading, temperature, voltage, resistance)
    
    # Save the time, current, temperature, voltage and resistance values in a file
    with open(fileName, "a") as f:      
        recording = csv.writer(f, delimiter = ',')
        recording.writerow([time.time()-start, current_reading, temperature, voltage, resistance])
    #f.close()
    
    # Close the connection with the instruments
    #rm.close()
    #fuji.serial.close()
    

    

        