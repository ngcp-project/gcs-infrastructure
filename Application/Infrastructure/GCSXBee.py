from Command import *
from Enum import *
from PacketLibrary.PacketLibrary import PacketLibrary
from Telemetry.Telemetry import Telemetry

import queue
import threading

from xbee import XBee

#PORT = "COM4"
BAUD_RATE = 115200

# 00 13 A2 00 42 43 5E A9
def StartXBee(PORT: str, CommandQueue: queue.Queue, TelemetryQueue: queue.Queue):
    # Initialize XBee object
    xbee = XBee(PORT, BAUD_RATE)

        # Open serial connection
    try:
        xbee.open()
    except Exception as e:
        print(f"Error: {e}")

    CommandStopEvent = threading.Event()
    TelemetryStopEvent = threading.Event()

    CommandThread = threading.Thread(target = RunCommandThread, args = (xbee, CommandQueue, CommandStopEvent))
    CommandThread.start()

    TelemetryThread = threading.Thread(target = RunTelemetryThread, args = (xbee, TelemetryQueue, TelemetryStopEvent))
    TelemetryThread.start()

def RunCommandThread(xbee: XBee, CommandQueue: queue.Queue, CommandStopEvent: threading.Event):
    while xbee is not None and xbee.ser is not None and not CommandStopEvent.is_set():
        try:
            Command = CommandQueue.get()

            if (isinstance(Command, CommandInterface)):
                EncodedCommand = Command.EncodePacket()

                CommandQueue.task_done()
            else:
                print("Not a command ")

                CommandQueue.task_done()
                    
                continue

            if (Command.Vehicle == Vehicle.ALL):
                xbee.transmit_data(EncodedCommand, PacketLibrary.MRA_MAC_ADDRESS)
                xbee.transmit_data(EncodedCommand, PacketLibrary.MEA_MAC_ADDRESS)
                xbee.transmit_data(EncodedCommand, PacketLibrary.ERU_MAC_ADDRESS)
            else:
                xbee.transmit_data(EncodedCommand, PacketLibrary.GetMACAddressFromVehicle(Command.Vehicle))

            #print("Data sent")

        except queue.Empty as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {e}")

    if (xbee is not None):
        xbee.close()

def RunTelemetryThread(xbee: XBee, TelemetryQueue: queue.Queue, TelemetryStopEvent: threading.Event):
    while xbee is not None and xbee.ser is not None and not TelemetryStopEvent.is_set():
        try:
            Data = xbee.retrieve_data()

            if Data:
                #print("Data received:\n")
                #print("Retrieved data:", data.received_data.decode("utf-8"))

                ReceivedTelemetry = Telemetry.Decode(Data.received_data)

                ReceivedTelemetry.Vehicle = PacketLibrary.GetVehicleFromMACAddress(Data.address_64.hex())
                ReceivedTelemetry.MACAddress = Data.address_64.hex()

                TelemetryQueue.put(ReceivedTelemetry)
                
        except queue.Empty as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {e}")

    if (xbee is not None):
        xbee.close()