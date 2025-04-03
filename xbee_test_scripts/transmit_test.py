import sys
sys.path.insert(1, '../')
# sys.path.append('C:/Users/alber/OneDrive/Рабочий стол/Olena/gcs-infrastructure')

import threading
from Logger.Logger import Logger
from Communication.XBee.XBee import XBee

# PORT = "COM5"
PORT = "/dev/cu.usbserial-D30DWZKY"
# PORT = "/dev/cu.usbserial-D30DWZL4"
BAUD_RATE = 115200
CONFIG_FILE = "AT_Command_List.txt"
# DESTINATION = "0013A20042435EA9"
# 00 13 A2 00 42 43 5E A9

LOGGER = Logger()
xbee = XBee(port=PORT, baudrate=BAUD_RATE, logger=LOGGER, config_file=CONFIG_FILE)
    
counter = 0
def func():
    global counter
    data = xbee.transmit_data("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" + str(counter), retrieveStatus=True)
    LOGGER.write("Sent AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" + str(counter))
    counter += 1

    print("Data sent")
    # data = xbee.retrieve_data()
    if data:
        print(f"transmit_test.py -> Retrieved data: Frame ID: {data.frame_id} Frame Type: {data.frame_type} Status: {data.status}")
        LOGGER.write(f"transmit_test.py -> Retrieved data: {data}")


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def main():
    print("XBEE TRANSMIT TEST")
    print("===============================")
    try:
        xbee.open()
    except Exception as e:
        print(f"Error: {e}")
        return
    
    set_interval(func, 1)

if __name__ == '__main__':
    main()