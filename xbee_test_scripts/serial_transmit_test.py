import sys
sys.path.insert(1, '../')
# sys.path.append('C:/Users/alber/OneDrive/Рабочий стол/Olena/gcs-infrastructure')

from Communication.XBee.XBee import XBee

PORT = "COM4"
#PORT = "/dev/cu.usbserial-D30DWZKY"
# PORT = "/dev/cu.usbserial-D30DWZL4"
BAUD_RATE = 115200
DESTINATION = "0013A200428396C0"
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

            xbee.transmit_data(data_to_send, DESTINATION)
            print("Data sent")
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

    # Transmit data
    # xbee.transmit_data("Hello, world!")
    # Receive data
    # print(xbee.receive_data())
    # Close serial connection
    xbee.close()

if __name__ == '__main__':
    main()