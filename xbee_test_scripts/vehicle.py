import sys
import threading
import time
from datetime import datetime

sys.path.insert(1, '../')

from Communication.XBee.XBee import XBee
from Communication.XBee.Frames.x81 import x81
from Logger.Logger import Logger

# Constants
TAG_COMMAND = 0x01
TAG_TELEMETRY = 0x02
TAG_ACK = 0x03

COMMANDS = {
    1: "KEEP_IN_ZONE",
    2: "EMERGENCY_STOP",
    3: "MOVE_TO_COORD",
    4: "RETURN_HOME"
}

#Vehicle Setup
VEHICLE_NAME = "MEA"  # Change this to the current vehicle: "MRA", "MEA", or "ERU"
GCS_MAC = "0013A200424366C7"  # MAC of the GCS XBee

logger = Logger(log_to_console = False)
vehicle_xbee = XBee(port="/dev/ttyUSB0", baudrate=115200, logger=logger)  # !!! set correct port !!!
vehicle_xbee.open()

# To send telemetry
def send_telemetry():
    count = 0
    while True:
        payload = chr(TAG_TELEMETRY) + f"{VEHICLE_NAME}::AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        vehicle_xbee.transmit_data(payload, address=GCS_MAC)
        #print(f"Sent telemetry: {payload[1:]}")  # Skipping tag when printing
        
        # Log only telemetry (no ACKs)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("vehicle_telemetry_log.txt", "a") as log_file:
            log_file.write(f"[{timestamp}] {payload[1:]}\n")
        
        count += 1
        time.sleep(1)

#To receive commands
def listen_for_commands():
    while True:
        frame: x81 = vehicle_xbee.retrieve_data()
        if frame:
            payload = frame.data.encode() if isinstance(frame.data, str) else frame.data
            tag = payload[0]
            body = payload[1:].decode()

            if tag == TAG_COMMAND:
                try: 
                    cmd_id = int(body)
                    cmd_name = COMMANDS.get(cmd_id, "UNKNOWN_COMMAND")
                    print(f"Received Command: [{cmd_id}] {cmd_name}")
        
                    ack_msg = chr(TAG_ACK) + str(cmd_id)
                    vehicle_xbee.transmit_data(ack_msg, address=GCS_MAC)
                    print(f"Sent ACK for command [{cmd_id}] {cmd_name}")
                except ValueError:
                    print(f"Failed to decode command ID from body: '{body}'")
        time.sleep(1)



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
