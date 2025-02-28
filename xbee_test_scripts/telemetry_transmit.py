import sys
import time

sys.path.append('/Users/olenamolla/Desktop/NGCP/gcs-infrastructure')
from Communication.XBee import XBee

from Communication.Telemetry import Telemetry  # Import the shared class



PORT = "/dev/tty.usbserial-D30DWZKT"
BAUD_RATE = 115200

def main():
    print("XBEE SERIAL TRANSMIT TEST")
    xbee = XBee(PORT, BAUD_RATE)

    if not xbee.open():
        return

    while True:
        try:
            # User input
            lat = float(input("Enter latitude: "))
            lon = float(input("Enter longitude: "))
            telemetry = Telemetry(lat, lon)

            # Optional XBee address
            address = input("Enter XBee address (leave empty for default 00000000): ")
            address = address if address else "00000000"

            print(f"Sending Telemetry: {telemetry} to Address: {address}")

            if xbee.transmit_telemetry(telemetry, address):
                print("Telemetry sent successfully!")
            else:
                print("Transmission failed.")

            time.sleep(1)  # Short delay before next transmission
        
        except Exception as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("Exiting...")
            xbee.close()
            return

if __name__ == '__main__':
    main()
