import sys
sys.path.insert(1, '../')

import threading
# from  multiprocessing import Process
# from pynput import keyboard

from Communication.XBee.XBee import XBee
from Logger.Logger import Logger
from Packet.Telemetry.Telemetry import Telemetry

PORT = "/dev/cu.usbserial-D30DWZKT" # Replace with your actual serial port. Plug in module and run "ls -l /dev/cu.usb*"
BAUD_RATE = 115200

transmit = False
transmit_lock = threading.Lock()
transmit_data = ""

logger = Logger(log_to_console = True)

def manage_serial(xbee: XBee):
    logger.write("STARTING TO RETRIEVE DATA")
    while xbee is not None and xbee.ser is not None:
        try:
            data = xbee.retrieve_data()
            global transmit
            if transmit:
                print("Sending: %s" % transmit_data)
                xbee.transmit_data(transmit_data)
                print("Data sent")
                transmit = False
            logger.write("AASDFASDF: ", getattr(data, "data", "No data received"))
            if data:
                logger.write(f"DATA RECEIVED>>>>>>>>>: {data.data}")
                decoded_data = Telemetry.decode(data.data)
                logger.write(f"Decoded data: {decoded_data}")
                print(decoded_data)
        except KeyboardInterrupt:
            return
        except Exception as e:
            print(f"Error: {e}")
            continue
    
def listen_keyboard():
    try:
        while True:
            global transmit_data, transmit
            transmit_data = input()
            # with transmit_lock:
            transmit = True
    except KeyboardInterrupt:
        return

def main():
    xbee = XBee(PORT, BAUD_RATE, logger=logger)

    try:
        xbee.open()
    except Exception as e:
        print(f"Error: {e}")

    t2 = threading.Thread(target=listen_keyboard)
    t1 = threading.Thread(target=manage_serial, args=(xbee,))

    t2.start()
    t1.start()
    t1.join()
    t2.join()

if __name__ == '__main__':
    main()