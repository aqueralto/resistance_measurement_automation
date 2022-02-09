# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 14:32:12 2021

@author: aqueralto
"""

#!/usr/bin/env python 
import os
import sys
import time
from threading import Thread
import serial
from serial.tools import list_ports
import minimalmodbus
import pyvisa
import pandas as pd
import numpy as np

   
# Functions for Fuji PXR4

# Define Function to Start Data Acquisition
# Measurement will not stop until program is stopped
def temperature_initialization():
    instrument = minimalmodbus.Instrument(mode = 'rtu', port = 'COM3', slaveaddress = 1, 
                                    close_port_after_each_call = True,
                                  debug = False)  # port name, slave address (in decimal)

    instrument.serial.baudrate = 9600 # Baud
    instrument.serial.bytesize = 8
    instrument.serial.parity = serial.PARITY_NONE
    instrument.serial.stopbits = 1
    instrument.serial.timeout = 1 # seconds
    instrument.clear_buffers_before_each_transaction = True
            
def temperature_measurement():
    temperature = instrument.read_register(0, 1, 4)
    
def temperature_finish():
    instrument.serial.close()
        
# Functions for the Keithley 2182

# Define Function to Start Data Acquisition
# Measurement will stop until program is stopped
def voltage_initialization():
    rm = pyvisa.ResourceManager()
    rm.open_resource('GPIB0::6::INSTR')
    rm.write("*rst; status:preset; *cls")
    rm.write(":INIT:CONT ON")
    rm.write("*WAI")

def voltage_measurement():
    voltage = rm.query(":READ?")

def voltage_finish():
    rm.query(":STAT:MEAS?")
    rm.write("TRAC:CLE; FEED:CONT:NEXT")
        
# Threading measurements

if __name__ == '__main__':
    voltage_initialization()
    temperature_initialization()
    
    # Loop for Data Acquisition
    while True:
        try:
            thread = Thread(target = temperature_measurement).start()
            thread = Thread(target = voltage_measurement).start()

            print(time.process_time(), temperature, voltage)
            
            with open("data.txt", "a") as f:
                recording = csv.writer(f, delimiter = ',')
                recording.writerow([time.process_time(), temperature, voltage])

        except:
            print("Keyboard Interrupt")
            break

    temperature_finish()
    voltage_finish()

        