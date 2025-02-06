import sys
sys.path.insert(1, '../')

# from Communication.XBee import XBee
from Logger.Logger import Logger

# PORT = "/dev/cu.usbserial-D30DWZKT"
# PORT = "/dev/cu.usbserial-D30DWZKY"
# BAUD_RATE = 115200

def main():
    print("XBEE SERIAL RECEIVE TEST")
    print("===============================")

    # Initialize XBee object
    # xbee = XBee(PORT, BAUD_RATE)
    logger = Logger()
    logger.write("1")
    logger.write("2")
    logger.write("3")
    logger.write("4")
        # Open serial connection
    # try:
    #     opened = xbee.open()
    #     # logger.write(f"Opening XBee connection... {"Success" if opened else "Failed"}")
    # except Exception as e:
    #     print(f"Error: {e}")
    #     # logger.write(f"Error: {e}")

    # while xbee is not None and xbee.ser is not None:
    #     try:
    #         data = xbee.retrieve_data()
    #         if data:
    #             print("Retrieved data:", data)
    #             # logger.write(f"Retrieved data:", data)
    #     except Exception as e:
    #         print(f"Error: {e}")
    #         # logger.write(f"Error: {e}")
    #     except KeyboardInterrupt:
    #         return
    #     # finally:
    #     #     # Close serial connection
    #     #     print("Closing serial connection...")
    #     #     xbee.close()
    #     #     return
    # xbee.close()
    # # logger.write("XBee connection closed")
        
if __name__ == '__main__':
    main()