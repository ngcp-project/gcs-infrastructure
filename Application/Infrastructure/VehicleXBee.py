from Command import *
from Enum import *
from Infrastructure.PacketQueue import *
from PacketLibrary.PacketLibrary import PacketLibrary
from Telemetry.Telemetry import Telemetry

import queue
import threading

from xbee import XBee
from logger import Logger

#PORT = "COM4"
BAUD_RATE = 115200

# 00 13 A2 00 42 43 5E A9
def StartVehicleXBee(PORT: str):
    # Initialize XBee object
    xbee = XBee(PORT, BAUD_RATE, logger=Logger(log_to_console=False))

        # Open serial connection
    try:
        xbee.open()
    except Exception as e:
        print(f"Error: {e}")

    CommandStopEvent = threading.Event()
    TelemetryStopEvent = threading.Event()

    CommandThread = threading.Thread(target = RunCommandThread, args = (xbee, CommandStopEvent))
    CommandThread.start()

    TelemetryThread = threading.Thread(target = RunTelemetryThread, args = (xbee, TelemetryStopEvent))
    TelemetryThread.start()

def RunCommandThread(xbee: XBee, CommandStopEvent: threading.Event):
    while xbee is not None and xbee.ser is not None and not CommandStopEvent.is_set():
        try:
            Data = xbee.retrieve_data()

            if Data:
                #print("Data received:\n")
                #print("Retrieved data:", data.received_data.decode("utf-8"))

                if (Data is not None):
                    CommandQueue.put(Data)
                
        except Exception as e:
            print(f"Error: {e}")

    if (xbee is not None):
        xbee.close()

def RunTelemetryThread(xbee: XBee, TelemetryStopEvent: threading.Event):
    while xbee is not None and xbee.ser is not None and not TelemetryStopEvent.is_set():
        try:
            TelemetryInstance = TelemetryQueue.get()

            if (isinstance(TelemetryInstance, Telemetry)):
                EncodedTelemetry = TelemetryInstance.Encode()

                TelemetryQueue.task_done()
            else:
                print("Not telemetry")

                TelemetryQueue.task_done()
                    
                continue

            xbee.transmit_data(EncodedTelemetry, PacketLibrary.GetGCSMACAddress())

            #print("Data sent")
                
        except queue.Empty as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {e}")

    if (xbee is not None):
        xbee.close()