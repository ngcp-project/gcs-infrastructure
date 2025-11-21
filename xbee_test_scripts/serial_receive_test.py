import sys
import os
#Get the absolute path to the parent directory

current_dir = os.path.dirname(os.path.abspath(__file__))    #this is what Kayshawn and I changed
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)

#changed above 3 lines^^

from Communication.XBee.XBee import XBee
# from Logs.Logger import Logger
from Logger.Logger import Logger

# PORT = "COM5"
#PORT = "/dev/cu.usbserial-D30DWZKY" #comment out
PORT = "COM7"
# PORT = "/dev/cu.usbserial-D30DWZL4"
BAUD_RATE = 115200
CONFIG_FILE = "AT_Command_List.txt"

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
        #cLogger.write(f"Opening XBee connection... {"Success" if opened else "Failed"}")


#Where the error starts 11/11/25

    except Exception as e:
        print(f"Error: {e}")
        # LOGGER.write(f"Error: {e}")
    print("Being to retrieve data:")
    while xbee is not None and xbee.ser is not None:
        try:
            data = xbee.retrieve_data()
            if data:
                print("Retrieved data:", data)
                Logger.write() #Logger from logger #previously commented 43 and 44
                LOGGER.write(f"Retrieved data:" + data[0] + " " + str(data[1]))
        except Exception as e:
            print(f"Error: {e}")
            # LOGGER.write(f"Error: {e}")
        except KeyboardInterrupt:
            return
        finally:                                    #uncommented from 50-54, new errors in file
             # Close serial connection
             print("Closing serial connection...") 
             xbee.close()
             return
    xbee.close()
    # LOGGER.write("XBee connection closed")
        
if __name__ == '__main__':
    main()