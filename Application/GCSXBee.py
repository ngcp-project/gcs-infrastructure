from Command.CommandInterface import CommandInterface
from Command.EmergencyStop import EmergencyStop
from Command.Heartbeat import Heartbeat
from Command.KeepIn import KeepIn
from Enum.ConnectionStatus import ConnectionStatus
from Telemetry.Telemetry import Telemetry

import ast
import queue
import threading

from xbee import XBee

#PORT = "COM4"
BAUD_RATE = 115200
DESTINATION = "0013A200428396C0"
# 00 13 A2 00 42 43 5E A9
def STARTXBee(PORT: str, CommandQueue: queue.Queue, TelemetryQueue: queue.Queue):
    print("XBEE SERIAL TRANSMIT TEST")
    print("===============================")
    
    # Initialize XBee object
    xbee = XBee(PORT, BAUD_RATE)

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

def RunCommandThread(xbee: XBee, CommandQueue: queue.Queue, CommandStopEvent: threading.Event):
    while xbee is not None and xbee.ser is not None and not CommandStopEvent.is_set():
        try:
            Command = CommandQueue.get()

            if (isinstance(Command, CommandInterface)):
                data_to_send = Command.encode_packet()
            else:
                print("Not a command ")

                CommandQueue.task_done()
                    
                continue

            #print("Sending: %s" % data_to_send)

            xbee.transmit_data(data_to_send, DESTINATION)

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
                print("Data received:\n")
                #print("Retrieved data:", data.received_data.decode("utf-8"))

                ReceivedTelemetry = Telemetry.decode(Data.received_data)

                print(ReceivedTelemetry)

                TelemetryQueue.put(ReceivedTelemetry)
                
        except queue.Empty as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {e}")

    if (xbee is not None):
        xbee.close()