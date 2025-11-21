import sys
import os
#Get the absolute path to the parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)


from Communication.XBee.XBee import XBee

# PORT = "COM5"
#PORT = "/dev/cu.usbserial-D30DWZKY" #CV: commented out and changed port to com7
PORT = "COM9"
# PORT = "/dev/cu.usbserial-D30DWZL4"
BAUD_RATE = 115200
DESTINATION = "0013A200424366C7" #CV: transmitting to COM7
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

    while xbee is not None and xbee.ser is not None:
        try:
            data_to_send = input()
            print("Sending: %s" % data_to_send)

            xbee.transmit_data(data_to_send, DESTINATION)   #up to here is fine I believe
            print("Data sent")
            data = xbee.retrieve_data()
            if data:
                print("Retrieved data:", data)
        
        except Exception as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            return
         #finally: 
             # Close serial connection
             #print("Closing serial connection...")
             #xbee.close()
             #return

    # Transmit data
    # xbee.transmit_data("Hello, world!")
    # Receive data
    # print(xbee.receive_data())
    # Close serial connection
    xbee.close()

if __name__ == '__main__':
    main()