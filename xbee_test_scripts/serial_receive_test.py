import sys
sys.path.insert(1, '../')
# sys.path.append('C:/Users/alber/OneDrive/Рабочий стол/Olena/gcs-infrastructure')
# print(sys.path)

from Communication.XBee import XBee
# from Logs.Logger import Logger

# PORT = "COM5"
# PORT = "/dev/cu.usbserial-D30DWZKY"
PORT = "/dev/cu.usbserial-D30DWZL4"
BAUD_RATE = 115200

def main():
    print("XBEE SERIAL RECEIVE TEST")
    print("===============================")

    # Initialize XBee object
    xbee = XBee(PORT, BAUD_RATE)
    # logger = Logger()
        # Open serial connection
    try:
        opened = xbee.open()
        # logger.write(f"Opening XBee connection... {"Success" if opened else "Failed"}")
    except Exception as e:
        print(f"Error: {e}")
        # logger.write(f"Error: {e}")

    while xbee is not None and xbee.ser is not None:
        try:
            data = xbee.retrieve_data()
            if data:
                print("Retrieved data:", data)
                # logger.write(f"Retrieved data:", data)
        except Exception as e:
            print(f"Error: {e}")
            # logger.write(f"Error: {e}")
        except KeyboardInterrupt:
            return
        # finally:
        #     # Close serial connection
        #     print("Closing serial connection...")
        #     xbee.close()
        #     return
    xbee.close()
    # logger.write("XBee connection closed")
        
if __name__ == '__main__':
    main()