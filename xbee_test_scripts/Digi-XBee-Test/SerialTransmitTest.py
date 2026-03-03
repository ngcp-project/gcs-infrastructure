import sys
sys.path.insert(1, '../')
# sys.path.append('C:/Users/alber/OneDrive/Рабочий стол/Olena/gcs-infrastructure')

from digi.xbee.devices import *

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
    LocalXBee = XBeeDevice(PORT, BAUD_RATE)

    RemoteXBee = RemoteXBeeDevice(LocalXBee, XBee64BitAddress.from_hex_string(DESTINATION))

        # Open serial connection
    try:
        LocalXBee.open()
    except Exception as e:
        print(f"Error: {e}")

    while LocalXBee is not None:
        try:
            OutgoingData = input()
            print("Sending: %s" % OutgoingData)

            LocalXBee.send_data(RemoteXBee, OutgoingData)
            print("Data sent")

            XBeeMessage = LocalXBee.read_data()
            if XBeeMessage:
                Data = XBeeMessage.data.decode("utf-8")

                print("Retrieved data:", Data)
        
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
    LocalXBee.close()

if __name__ == '__main__':
    main()