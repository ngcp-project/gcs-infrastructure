import sys
import threading
sys.path.append('/Users/olenamolla/Desktop/NGCP/gcs-infrastructure')

from Communication.XBee.XBee import XBee
from Communication.XBee.Frames.x81 import x81
from Logger.Logger import Logger

import time


# Constants
TAG_COMMAND = 0x01
TAG_TELEMETRY = 0x02
TAG_ACK = 0x03

# Defining known vehicles

VEHICLES = {
    
    "MRA": {
        "MAC": "0013A200424353F7",
        "short": "0002"
    },
    
    "ERU": {
        "MAC": "NaN",
        "short": "0003"
    },
    
    "MEA": {
        "MAC": "0013A2004243672F",
        "short": "0004"
    }
}

COMMANDS = {
    1: "KEEP_IN_ZONE",
    2: "EMERGENCY_STOP",
    3: "MOVE_TO_COORD",
    4: "RETURN_HOME"
}

# Initializing XBee GCS

logger = Logger()
gcs_xbee = XBee(port="/dev/cu.usbserial-D30DWZKT", baudrate=115200, logger=logger) # !!! set correct port !!!
gcs_xbee.open()

def listen_for_telemetry():
   while True:
        frame: x81 = gcs_xbee.retrieve_data()
        if frame:
            payload = frame.data  # already a str due to decode in XBee library
            src_16bit = frame.source_address.hex().upper().zfill(4)

            tag = ord(payload[0])       # convert first character to byte tag
            body = payload[1:]          # everything after the tag

            if tag == TAG_ACK:
                print(f"Received ACK from {src_16bit}: {body}")
            elif tag == TAG_TELEMETRY:
                log_line = f"[Telemetry] From: {src_16bit}, RSSI: {frame.rssi}, Data: {body}\n"
                with open("gcs_telemetry_log.txt", "a") as log_file:
                    log_file.write(log_line)
        time.sleep(0.05)
        
        

def main():
    
    telemetry_thread = threading.Thread(target=listen_for_telemetry, daemon=True)
    telemetry_thread.start()
    
    
    # Placeholder for commands logic
    
    try:
        while True:
            # for now just wait
            print("\nGCS Commands")
            print("Available Vehicles: ", ", ".join(VEHICLES.keys()))
            vehicle_name = input("Enter vehicle name (or 'exit' to quit): \n\n").strip().upper()
            
            if vehicle_name == 'EXIT':
                break
            
            if vehicle_name not in VEHICLES:
                print("Invalid Vehicle Name.")
                continue
            
            vehicle = VEHICLES[vehicle_name]
            
            if vehicle["MAC"] == "NaN":
                print("MAC address not set for this vehicle.")
                continue
            
            print ("Available Commands:")
            for cmd_id, cmd_name in COMMANDS.items():
                print(f" {cmd_id}: {cmd_name}")
                
                
            try:
                command_id = int(input("Enter Command ID: "))
                if command_id not in COMMANDS:
                    print("Invalid Command ID")
                    continue
            except ValueError:
                print("Invalid Input")
                continue
            
            
            payload = chr(TAG_COMMAND) + str(command_id)
            print(f"Sending '{COMMANDS[command_id]}' (ID={command_id}) to {vehicle_name}")
            status = gcs_xbee.transmit_data(payload, address=vehicle["MAC"], retrieveStatus=True)
            
            if status:
                print("Transmit status received.")
            else:
                print(f"No transmit status.")
            
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n Exiting...")
        
        
if __name__ == "__main__":
    main()