import sys
sys.path.insert(1, '../')

import threading
# from  multiprocessing import Process
# from pynput import keyboard

from Communication.XBee.XBee import XBee

# PORT = "/dev/cu.usbserial-D30DWZL4" # Replace with your actual serial port. Plug in module and run "ls -l /dev/cu.usb*"
PORT = "/dev/cu.usbserial-D30DWZKY"
BAUD_RATE = 115200

transmit = False
transmit_lock = threading.Lock()
transmit_data = ""

def manage_serial(xbee:XBee):
    try:
        while xbee is not None and xbee.ser is not None:
            data = xbee.retrieve_data()
            global transmit 
            if transmit == True:
                print("Sending: %s" % transmit_data)
                xbee.transmit_data(transmit_data)
                print("Data sent")
                # with transmit_lock:
                transmit = False
            if data:
                print("Retrieved data:", data)
            
    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        return
    
def listen_keyboard():
    try:
        while True:
            global transmit_data, transmit
            transmit_data = input()
            print("asdf")
            # with transmit_lock:
            transmit = True
    except KeyboardInterrupt:
        return

def main():
    xbee = XBee(PORT, BAUD_RATE)

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