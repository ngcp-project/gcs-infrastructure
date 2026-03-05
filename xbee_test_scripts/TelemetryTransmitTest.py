from Command.Heartbeat import Heartbeat
from Command.EmergencyStop import EmergencyStop
from Telemetry.Telemetry import Telemetry
from Enum.ConnectionStatus import ConnectionStatus

import json
import sys
import threading
import time
sys.path.insert(1, '../')

# sys.path.append('C:/Users/alber/OneDrive/Рабочий стол/Olena/gcs-infrastructure')
# print(sys.path)

from xbee import XBee
# from Logs.Logger import Logger
from logger import Logger

PORT = "COM3"
BAUD_RATE = 115200
DESTINATION = "0013A2004283A0EC"
#CONFIG_FILE = "AT_Command_List.txt"
CONFIG_FILE = ""

LOGGER = Logger()

def main():
    print("XBEE SERIAL RECEIVE TEST")
    print("===============================")

    # Initialize XBee object
    xbee = XBee(port=PORT, baudrate=BAUD_RATE, logger=LOGGER, config_file=CONFIG_FILE)
        # Open serial connection
    try:
        opened = xbee.open()
        # LOGGER.write("XBee Opened")
        # logger.write(f"Opening XBee connection... {"Success" if opened else "Failed"}")
    except Exception as e:
        print(f"Error: {e}")
        # LOGGER.write(f"Error: {e}")
    print("Listening for data:")

    StopEvent = threading.Event()

    thread = threading.Thread(target = ListenForData, args = (xbee, StopEvent))
    thread.start()

    while xbee is not None and xbee.ser is not None:
        try:
            time.sleep(1)
        except Exception as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("Closing thread")

            StopEvent.set()
            thread.join()

            print("Closing serial connection...")

            break
    
    if (xbee is not None):
        xbee.close()

        # finally:
        #     # Close serial connection
        #     print("Closing serial connection...")
        #     xbee.close()
        #     return
    #xbee.close()
    # LOGGER.write("XBee connection closed")

def ListenForData(xbee: XBee, StopEvent: threading.Event):
    while xbee is not None and xbee.ser is not None and not StopEvent.is_set():
        try:
            data = xbee.retrieve_data()
            if data:
                Command = None

                match(data.received_data[0]):
                    case 1:
                        Command = Heartbeat.decode_packet(data.received_data)
                    case 2:
                        Command = EmergencyStop.decode_packet(data.received_data)
                    case _:
                        print("\nRetrieved data:", data.received_data.decode("utf-8"))

                if (Command is not None):
                    print(f"\n{Command}")

                try:
                    TelemetryData = json.loads(Command)
                    
                except json.JSONDecodeError as e:
                    print(f"JSON Error {e}")

                telem = Telemetry(TelemetryData["Command ID"], TelemetryData["Packet ID"], 0, 0, 0, 0, 0, 0.8, 0, (1, 2), 0, 0, 1.0, 1.0, 0)

                data_to_send = telem.encode()

                xbee.transmit_data(data_to_send, DESTINATION)
                # logger.write()
                # LOGGER.write(f"Retrieved data:" + data[0] + " " + str(data[1]))
        except Exception as e:
            print(f"Error: {e}")
            # LOGGER.write(f"Error: {e}")
        #except KeyboardInterrupt:
            #return
        
if __name__ == '__main__':
    main()