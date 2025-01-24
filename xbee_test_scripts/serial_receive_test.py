import sys
sys.path.insert(1, '../')

from Communication.XBee import XBee

PORT = "/dev/cu.usbserial-D30DWZKT"
BAUD_RATE = 115200

def main():
    print("XBEE SERIAL RECEIVE TEST")
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
            data = xbee.retrieve_data()
            if data:
                print("Retrieved data:", data)
        except Exception as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            return
        # finally:
        #     # Close serial connection
        #     print("Closing serial connection...")
        #     xbee.close()
        #     return
        
if __name__ == '__main__':
    main()