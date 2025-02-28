import sys
import time
sys.path.append('/Users/olenamolla/Desktop/NGCP/gcs-infrastructure')
from Communication.XBee import XBee
from Communication.Telemetry import Telemetry  # Import the shared class

PORT = "/dev/tty.usbserial-D30DWZKT"
import sys
from Communication.XBee import XBee
from Communication.Telemetry import Telemetry

PORT = "/dev/tty.usbserial-D30DWZL4"
BAUD_RATE = 115200

def main():
    print("XBEE SERIAL RECEIVE TEST")
    print("===============================")
    
    xbee = XBee(PORT, BAUD_RATE)

    if not xbee.open():
        return

    while True:
        try:
            binary_data, frame_data = xbee.receive_binary()  # Get raw binary telemetry packet
            
            if binary_data:
                if len(binary_data) == 53:  # Ensure correct packet size
                    telemetry = Telemetry.decode(binary_data)
                    print(f"\n[DEBUG] Decoded Telemetry: {telemetry}")
                else:
                    print(f"[ERROR] Received invalid packet size: {len(binary_data)} bytes")

        except Exception as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("Exiting...")
            xbee.close()
            return

if __name__ == '__main__':
    main()
