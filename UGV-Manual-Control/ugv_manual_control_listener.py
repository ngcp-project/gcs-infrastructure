import ast
import sys
import threading
import time
from datetime import datetime
# from ugv import man_ctrl

sys.path.insert(1, "../")
# sys.path.append('/Users/olenamolla/Desktop/NGCP/gcs-infrastructure')

from Communication.XBee.XBee import XBee
from Communication.XBee.Frames.x81 import x81
from Logger.Logger import Logger

# Constants
TAG_COMMAND = 0x01
TAG_TELEMETRY = 0x02
TAG_ACK = 0x03

COMMANDS = {
    5: "MANUAL_CONTROL",
}

#Vehicle Setup
VEHICLE_NAME = "MRA"  # Change this to the current vehicle: "MRA", "MEA", or "ERU"
GCS_MAC = "0013A20042435A3D"  # MAC of the GCS XBee

logger = Logger(log_to_console = False)
vehicle_xbee = XBee(port="COM4", baudrate=115200, logger=logger)  # !!! set correct port !!!
vehicle_xbee.open()

last_sent_time = time.time()

#To receive commands
def listen_for_commands():
    while True:
        frame: x81 = vehicle_xbee.retrieve_data()
        if frame:
            payload = frame.data.encode() if isinstance(frame.data, str) else frame.data
            tag = payload[0]
            cmd = payload.decode()[1]
            body = payload.decode()[2:]

            if tag == TAG_COMMAND:
                try:
                    cmd_id = int(cmd)
                    cmd_name = COMMANDS.get(cmd_id, "UNKNOWN_COMMAND")
                    print(f"Received Command: [{cmd_id}] {cmd_name}")
                            
                    ack_msg = chr(TAG_ACK) + str(cmd_id)
                    vehicle_xbee.transmit_data(ack_msg, address=GCS_MAC)
                    print(f"Sent ACK for command [{cmd_id}] {cmd_name}")
                    
                    ### TODO: Write received data to UGV SW
                    body = ast.literal_eval(body)
                    """
                    # uncomment man_ctrl import
                    man_obj = man_ctrl()
                    man_obj.auto_en = body[0]
                    man_obj.linear_vel = body[1]
                    man_obj.steer_val = body[2]
                    man_obj.arm_cmd = body[3]
                    
                    man_writer.write(man_obj)
                    """

                    last_sent_time = time.time()
                    
                except ValueError:
                    print(f"Failed to decode command ID from body: '{body}'")
        else:
            curr_time = time.time()
            if(curr_time - last_sent_time >= 1):
                ### TODO: Write Stall/Stop data to UGV SW
                print("Stopping")
        time.sleep(0.1)



def main():
    thread = threading.Thread(target=listen_for_commands, daemon=True)
    thread.start()

    print("Listening for manual control...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        vehicle_xbee.close()

if __name__ == "__main__":
    main()
