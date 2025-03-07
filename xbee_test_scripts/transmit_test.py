import sys
sys.path.insert(1, '../')
# sys.path.append('C:/Users/alber/OneDrive/Рабочий стол/Olena/gcs-infrastructure')

import threading
from Logger.Logger import Logger
from Communication.XBee.XBee import XBee

# PORT = "COM5"
PORT = "/dev/cu.usbserial-D30DWZL4"
BAUD_RATE = 115200
# DESTINATION = "0013A20042435EA9"
# 00 13 A2 00 42 43 5E A9

xbee = XBee(PORT, BAUD_RATE)
logger = Logger()

try:
    xbee.open()
except Exception as e:
    print(f"Error: {e}")
counter = 0
def func():
    global counter
    xbee.transmit_data("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" + str(counter))
    logger.write("Sent AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" + str(counter))
    counter += 1

    print("Data sent")
    data = xbee.retrieve_data()
    if data:
        print("Retrieved data:", data)
        logger.write(data)


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
    
    set_interval(func, 1)

if __name__ == '__main__':
    main()