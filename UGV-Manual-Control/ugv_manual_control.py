
# (c) Copyright, Real-Time Innovations, 2022.  All rights reserved.
# RTI grants Licensee a license to use, modify, compile, and create derivative
# works of the software solely for use with RTI Connext DDS. Licensee may
# redistribute copies of the software provided that all such copies are subject
# to this license. The software is provided "as is", with no warranty of any
# type, including any warranty for fitness for any purpose. RTI is under no
# obligation to maintain or support the software. RTI shall not be liable for
# any incidental or consequential damages arising out of the use or inability
# to use the software.
import sys
sys.path.insert(1, "../")

import time
from inputs import get_gamepad
from Communication.XBee.XBee import XBee
from Communication.XBee.Frames.x81 import x81

SCALE_FACTOR = -32700
MAX_JOY_VAL = 2**15 # max input of 32,768
LOWER_ELBOW_SERV_LIM = -360.0
UPPER_ELBOW_SERV_LIM = 360.0
DEAD_ZONE_THRESH = 15/100
UPPER_STEER_CMD_LIMIT = 1.0

auto_en = False
linear_vel = 0.0
steer_val = 0.0
arm_cmd = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # Ten wide arm commands 

cmd_vel = 0
cmd_steer = 0
l_bumper = 0
r_bumper = 0
lt_val = 0
rt_val = 0
ud_dpad = 0
lr_dpad = 0
a_btn = 0

TAG_COMMAND = 0x01
TAG_TELEMETRY = 0x02
TAG_ACK = 0x03

VEHICLES = {
    "MRA": {
        "MAC": "0013A200424353F7",
        "short": "0002"
    },
}

COMMANDS = {
    5: "MANUAL_CONTROL"
}

vehicle_name = "MRA"
command_id = 5

gcs_xbee = XBee(port="COM3", baudrate=115200) # !!! set correct port !!!
gcs_xbee.open()


def send_manual_control_message():
    global auto_en
    global linear_vel
    global arm_cmd
    global l_bumper
    global r_bumper
    global lt_val
    global rt_val
    global ud_dpad
    global lr_dpad
    global a_btn
    
    vehicle = VEHICLES["MRA"]
    
    # add payload details
    print("auto_en:", auto_en)
    print("linear_vel:", linear_vel)
    print("arm_cmd:", arm_cmd)
    print("l_bumper:", l_bumper)
    print("r_bumper:", r_bumper)
    print("lt_val:", lt_val)
    print("rt_val:", rt_val)
    print("ud_dpad:", ud_dpad)
    print("lr_dpad:", lr_dpad)
    print("a_btn:", a_btn)
    
    payload = chr(TAG_COMMAND) + str(command_id)
    print(f"Sending '{COMMANDS[command_id]}' (ID={command_id}) to {vehicle_name}")
    status = gcs_xbee.transmit_data(payload, address=vehicle["MAC"], retrieveStatus=True)
    
    if status:
        print("Transmit status received.")
        print("Frame ID: ", status.frame_id, "Status: ", status.status)
    else:
        print(f"No transmit status.")

        
def main():
    global cmd_vel
    global cmd_steer
    global rt_val
    global lt_val
    global ud_dpad
    global lr_dpad
    
    try:
        print("Starting UGV Manual Control...")
        time_interval = 0.333
        marked_time = time.time()

        while(True):
            curr_time = time.time()
            event1 = get_gamepad()
            is_motion = False
            is_valid_input = True
            
            print("mark")
                        
            if event1[0].code == "ABS_Y":
                cmd_vel = event1[0].state/(MAX_JOY_VAL)
                if -DEAD_ZONE_THRESH <= cmd_vel and cmd_vel <= DEAD_ZONE_THRESH:
                    cmd_vel = 0
                is_motion = True
            elif event1[0].code == "ABS_RX":
                cmd_steer = event1[0].state/(-MAX_JOY_VAL)
                if -DEAD_ZONE_THRESH <= cmd_steer and cmd_steer <= DEAD_ZONE_THRESH:
                    cmd_steer = 0
                if cmd_steer > UPPER_STEER_CMD_LIMIT:
                    cmd_steer = UPPER_STEER_CMD_LIMIT
                is_motion = True
            
            ## Commands for payload arm actuation
            elif event1[0].code == "ABS_Z":
                lt_val = event1[0].state

            elif event1[0].code == "ABS_RZ":
                rt_val = event1[0].state

            elif event1[0].code == "ABS_HAT0Y":
                ud_dpad = event1[0].state
        
            elif event1[0].code == "ABS_HAT0X":
                lr_dpad = event1[0].state
            
            ## Commands to signal Autonomous enable. Autonous enable not implemented yet
            elif event1[0].code == 'BTN_TR':
                r_bumper = event1[0].state
                print("Right bumper action")

            elif event1[0].code == 'BTN_TL':
                l_bumper = event1[0].state
                print("Left bumper action")

            # if l_bumper == 1 and r_bumper == 1:
            #     if event1[0].code == "BTN_SOUTH"
            
            else: is_valid_input = False
            
            # Sends all Button inputs
            if(is_valid_input and not is_motion):
                send_manual_control_message()
            # Sends motion inputs over time interval
            elif(is_motion and curr_time - marked_time >= time_interval):
                send_manual_control_message()
                marked_time = curr_time
            
    finally:
        print("Preparing to shut down UGV Manual Control...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("UGV Manual Control Shut Down")
    except Exception as e:
        print("Error during UGV Manual Control process: ", e)
