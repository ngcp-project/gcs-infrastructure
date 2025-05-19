import sys
sys.path.insert(1, "../")

from datetime import datetime
import time
import threading

from Packet.Telemetry.Telemetry import Telemetry

from Communication.XBee.XBee import XBee
# from Communication.XBee.Frames.x81 import x81
from Logger.Logger import Logger

shared_telemetry = Telemetry()
telemetry_lock = threading.Lock()

#Vehicle Setup
VEHICLE_NAME = "ERU"  # Change this to the current vehicle: "MRA", "MEA", or "ERU"
GCS_MAC = "0013A200424366C7"  # MAC of the GCS XBee

logger = Logger(log_to_console = False)
vehicle_xbee = XBee(port="/dev/cu.usbserial-D30DWZL4", baudrate=115200, logger=logger)  # !!! set correct port !!!
vehicle_xbee.open()

def update_telemetry_data(speed=0, pitch=0, yaw=0, roll=0, altitude=0, battery_life=0,
             current_latitude=0, current_longitude=0, vehicle_status=0,
             patient_status=0,  # <-- move this up
             message_flag=0, message_lat=0.0, message_lon=0.0):
    with telemetry_lock:
        shared_telemetry.speed = speed
        shared_telemetry.pitch = pitch
        shared_telemetry.yaw = yaw
        shared_telemetry.roll = roll
        shared_telemetry.altitude = altitude
        shared_telemetry.battery_life = battery_life
        shared_telemetry.current_latitude = current_latitude
        shared_telemetry.current_longitude = current_longitude
        shared_telemetry.vehicle_status = vehicle_status
        shared_telemetry.patient_status = patient_status
        shared_telemetry.message_flag = message_flag
        shared_telemetry.message_lat = message_lat
        shared_telemetry.message_lon = message_lon
        shared_telemetry.last_updated = datetime.now().timestamp()

def update_telemetry():
    while True:
        print("updating...")
        # Use static variables to keep state between calls
        if not hasattr(update_telemetry, "speed"):
            update_telemetry.speed = 0
            update_telemetry.pitch = 0
            update_telemetry.yaw = 0
            update_telemetry.roll = 0
            update_telemetry.altitude = 0
            update_telemetry.battery_life = 1.0
            update_telemetry.current_latitude = 40.0
            update_telemetry.current_longitude = -74.0
            update_telemetry.vehicle_status = 0
            update_telemetry.patient_status = 0
            update_telemetry.message_flag = 0
            update_telemetry.message_lat = 40.0
            update_telemetry.message_lon = -74.0

        # Increment values
        update_telemetry.speed += 1
        update_telemetry.pitch += 1
        update_telemetry.yaw += 1
        update_telemetry.roll += 1
        update_telemetry.altitude += 1

        # Keep battery_life between 0 and 1, decrease by 0.01, reset to 1 if below 0
        update_telemetry.battery_life -= 0.01
        if update_telemetry.battery_life < 0:
            update_telemetry.battery_life = 1.0

        # Increment lat/lon slightly
        update_telemetry.current_latitude += 0.0001
        update_telemetry.current_longitude += 0.0001

        # Alternate vehicle_status and patient_status between 0 and 1
        update_telemetry.vehicle_status = 1 - update_telemetry.vehicle_status
        update_telemetry.patient_status = 1 - update_telemetry.patient_status

        # Increment message_flag, lat, lon
        update_telemetry.message_flag = (update_telemetry.message_flag + 1) % 2
        update_telemetry.message_lat += 0.0001
        update_telemetry.message_lon += 0.0001

        update_telemetry_data(
            speed=update_telemetry.speed,
            pitch=update_telemetry.pitch,
            yaw=update_telemetry.yaw,
            roll=update_telemetry.roll,
            altitude=update_telemetry.altitude,
            battery_life=update_telemetry.battery_life,
            current_latitude=update_telemetry.current_latitude,
            current_longitude=update_telemetry.current_longitude,
            vehicle_status=update_telemetry.vehicle_status,
            patient_status=update_telemetry.patient_status,
            message_flag=update_telemetry.message_flag,
            message_lat=update_telemetry.message_lat,
            message_lon=update_telemetry.message_lon
        )
        time.sleep(1)



def send_telemetry():
    logger.write("Starting to send telemetry data...")
    while True:
        print(f"Sending: {shared_telemetry}")
        logger.write(f"Sending: {shared_telemetry}")
        with telemetry_lock:
            telemetry_data = shared_telemetry.encode()
        
        # payload = telemetry_data.hex()
        # logger.write(f"payload: {payload}")
        # Convert payload (bytes) to a hex string for transmission
        # logger.write(f"payload bytes: {payload}")
        vehicle_xbee.transmit_data(telemetry_data, address=GCS_MAC, isByteString=True) # Add bytes parameter to prevent encoding of data that is already bytes.

        # timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        time.sleep(1)  # Transmission rate

def main():
    print("Starting threads...")
    logger.write("Starting threads...")
    telemetry_thread = threading.Thread(target=send_telemetry, daemon=True)
    update_thread = threading.Thread(target=update_telemetry, daemon=True)

    telemetry_thread.start()
    update_thread.start()
    
    telemetry_thread.join()
    update_thread.join()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        vehicle_xbee.close()

if __name__ == "__main__":
    main()