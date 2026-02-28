import sys
import threading
import time
sys.path.insert(1, '../')
# sys.path.append('C:/Users/alber/OneDrive/Рабочий стол/Olena/gcs-infrastructure')
# print(sys.path)

from digi.xbee.devices import *
# from Logs.Logger import Logger
from Logger.Logger import Logger

PORT = "COM3"
#PORT = "/dev/cu.usbserial-D30DWZKY"
# PORT = "/dev/cu.usbserial-D30DWZL4"
BAUD_RATE = 115200
#CONFIG_FILE = "AT_Command_List.txt"
CONFIG_FILE = ""

LOGGER = Logger()

def main():
    print("XBEE SERIAL RECEIVE TEST")
    print("===============================")

    # Initialize XBee object
    LocalXBee = XBeeDevice(PORT, BAUD_RATE)
        # Open serial connection
    try:
        LocalXBee.open()
        # LOGGER.write("XBee Opened")
        # logger.write(f"Opening XBee connection... {"Success" if opened else "Failed"}")
    except Exception as e:
        print(f"Error: {e}")
        # LOGGER.write(f"Error: {e}")
    print("Being to retrieve data:")

    StopEvent = threading.Event()

    thread = threading.Thread(target = ListenForData, args = (LocalXBee, StopEvent))
    thread.start()

    #while xbee is not None and xbee.ser is not None:
    try:
        while True:
            time.sleep(1)
            #data = xbee.retrieve_data()
            #if data:
                #print("Retrieved data:", data)
                # logger.write()
                # LOGGER.write(f"Retrieved data:" + data[0] + " " + str(data[1]))
    except Exception as e:
        print(f"Error: {e}")
            # LOGGER.write(f"Error: {e}")
    except KeyboardInterrupt:
        print("Closing thread")

        StopEvent.set()
        thread.join()

        print("Closing serial connection...")

        LocalXBee.close()

        return
        # finally:
        #     # Close serial connection
        #     print("Closing serial connection...")
        #     xbee.close()
        #     return
    #xbee.close()
    # LOGGER.write("XBee connection closed")

def ListenForData(LocalXBee: XBeeDevice, StopEvent: threading.Event):
    while LocalXBee is not None and not StopEvent.is_set():
        try:
            XBeeMessage = LocalXBee.read_data()
            if XBeeMessage:
                Data = XBeeMessage.data.decode("utf-8")

                print("Retrieved data:", Data)
                # logger.write()
                # LOGGER.write(f"Retrieved data:" + data[0] + " " + str(data[1]))
        except Exception as e:
            print(f"Error: {e}")
            # LOGGER.write(f"Error: {e}")
        #except KeyboardInterrupt:
            #return
        
if __name__ == '__main__':
    main()