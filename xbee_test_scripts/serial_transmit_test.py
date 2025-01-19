import sys
sys.path.insert(1, '../')

from Communication.XBee import XBee

PORT = "/dev/cu.usbserial-D30DWZL4"
BAUD_RATE = 115200

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

            xbee.transmit_data(data_to_send)
            print("Data sent")
        
        except Exception as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            return
        # finally:
        #     # Close serial connection
        #     print("Closing serial connection...")
        #     xbee.close()
        #     return

    # Transmit data
    # xbee.transmit_data("Hello, world!")
    # Receive data
    # print(xbee.receive_data())
    # Close serial connection
    # xbee.close()

if __name__ == '__main__':
    main()