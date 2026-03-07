from Command.EmergencyStop import EmergencyStop
from Command.Heartbeat import Heartbeat
from Command.KeepIn import KeepIn
from Enum.ConnectionStatus import ConnectionStatus
from Telemetry.Telemetry import Telemetry

import ast
import sys
import threading
sys.path.insert(1, '../')
# sys.path.append('C:/Users/alber/OneDrive/Рабочий стол/Olena/gcs-infrastructure')

from xbee import XBee

PORT = "COM4"
BAUD_RATE = 115200
DESTINATION = "0013A200428396C0"
# 00 13 A2 00 42 43 5E A9
def main():
    print("XBEE SERIAL TRANSMIT TEST")
    print("===============================")
    
    # Initialize XBee object
    xbee = XBee(PORT, BAUD_RATE)

        # Open serial connection
    try:
        xbee.open()
    except Exception as e:
        print(f"Error: {e}")

    #StopEvent = threading.Event()

    #thread = threading.Thread(target = ListenForData, args = (xbee, StopEvent))
    #thread.start()

    while xbee is not None and xbee.ser is not None:
        try:
            data_to_send = input()

            Command = ProcessCommand(data_to_send)

            if (Command is not None):
                data_to_send = Command.encode_packet()
            else:
                data_to_send.encode()

            print("Sending: %s" % data_to_send)

            xbee.transmit_data(data_to_send, DESTINATION)

            print("Data sent")

            data = xbee.retrieve_data()

            if data:
                print("Data received:\n")
                #print("Retrieved data:", data.received_data.decode("utf-8"))

                telem = Telemetry.decode(data.received_data)

                print(telem)
        
        except Exception as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:

            print("Closing thread")

            #StopEvent.set()
            #thread.join()

            print("Closing serial connection...")

            break

    if (xbee is not None):
        xbee.close()

def ProcessCommand(Command: str):
    if ((Command.replace(" ", "").upper() == "HEARTBEAT") or (Command == "1")):
        return HeartbeatCommand()
    elif ((Command.replace(" ", "").upper() == "EMERGENCYSTOP") or (Command == "2")):
        return EmergencyStopCommand()
    elif ((Command.replace(" ", "").upper() == "KEEPIN") or (Command == "3")):
        return KeepInCommand()
    
    return None

def HeartbeatCommand():
    print("Heartbeat Command\nEnter Connection Status:")

    while True:
        Input = input()

        if ((Input.upper() == "CONNECTED") or (Input == "0")):
            return Heartbeat(ConnectionStatus.Connected)
        elif ((Input.upper() == "UNSTABLE") or (Input == "1")):
            return Heartbeat(ConnectionStatus.Unstable)
        elif ((Input.upper() == "DISCONNECTED") or (Input == "2")):
            return Heartbeat(ConnectionStatus.Disconnected)

def KeepInCommand():
    print("Keep In Command\nEnter up to 6 coordinates:")

    Coordinates = []
    CoordinateCount = 1

    while True:
        print(f"Enter Coordinate {CoordinateCount} as (x, y), or q to end:")

        Input = input()

        try:
            if (CoordinateCount <= 6):
                if (Input.upper() == "Q"):
                    return KeepIn(Coordinates)

                Coordinate = ast.literal_eval(Input)

                print(Coordinate)

                Coordinates.append(Coordinate)

                CoordinateCount += 1
            else:
                return KeepIn(Coordinates)
        except Exception:
            print("Invalid tuple")
        
def EmergencyStopCommand():
    print("Emergency Stop Command\nEnter Stop Status:")

    while True:
        Input = input()

        try:
            StopStatus = int(Input)

            return EmergencyStop(StopStatus)
        except ValueError:
            print("Integer Required")

def ListenForData(xbee: XBee, StopEvent: threading.Event):
    while xbee is not None and xbee.ser is not None and not StopEvent.is_set():
        try:
            data = xbee.retrieve_data()
            if data:
                print("Data received")
                #print("Retrieved data:", data.received_data.decode("utf-8"))

                telem = Telemetry.decode(data.received_data)

                print(telem)

        except Exception as e:
            print(f"Error: {e}")


if __name__ == '__main__':
    main()