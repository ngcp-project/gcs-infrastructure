import sys
import threading
import time

sys.path.append('/Users/olenamolla/Desktop/NGCP/gcs-infrastructure')

from Communication.XBee.XBee import XBee
from Communication.XBee.Frames.x81 import x81
from Logger.Logger import Logger

#Vehicle Setup
VEHICLE_NAME = "MRA"  # Change this to the current vehicle: "MRA", "MEA", or "ERU"
GCS_MAC = "0013A200424366C7"  # MAC of the GCS XBee

logger = Logger()
vehicle_xbee = XBee(port="/dev/cu.usbserial-D30DX9UD", baudrate=115200, logger=logger)  # !!! set correct port !!!
vehicle_xbee.open()

# To send telemetry
def send_telemetry():
    count = 0
    while True:
        telemetry = f"{VEHICLE_NAME}::alt={100 + count};bat={90 - count%10}"
        vehicle_xbee.transmit_data(telemetry, address=GCS_MAC)
        print(f"Sent telemetry: {telemetry}")
        
        # Log only telemetry (no ACKs)
        with open("vehicle_telemetry_log.txt", "a") as log_file:
            log_file.write(f"{telemetry}\n")
        
        count += 1
        time.sleep(10)

#To receive commands
def listen_for_commands():
    while True:
        frame: x81 = vehicle_xbee.retrieve_data()
        if frame:
            try:
                command_id = frame.data.strip()
                
                print(f"Received Command ID: {command_id}")

                # Respond with ACK
                ack = f"ACK:{command_id}"
                vehicle_xbee.transmit_data(ack, address=GCS_MAC)
                print(f"Sent ACK for command {command_id}")

            except Exception as e:
                print(f"Error parsing command: {e}")
        time.sleep(0.05)



def main():
    telemetry_thread = threading.Thread(target=send_telemetry, daemon=True)
    command_thread = threading.Thread(target=listen_for_commands, daemon=True)

    telemetry_thread.start()
    command_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        vehicle_xbee.close()

if __name__ == "__main__":
    main()
