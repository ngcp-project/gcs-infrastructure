import struct

class Telemetry:
    """Handles telemetry data encoding and decoding for UAV/UGV communication."""
    
    def __init__(self, speed, pitch, yaw, roll, altitude, battery_life, last_updated,
             current_latitude, current_longitude, vehicle_status,
             patient_status,  # <-- move this up
             message_flag=0, message_lat=0.0, message_lon=0.0):
        self.speed = speed
        self.pitch = pitch
        self.yaw = yaw
        self.roll = roll
        self.altitude = altitude
        self.battery_life = battery_life
        self.last_updated = last_updated  # Timestamp (8 bytes)
        self.current_latitude = current_latitude
        self.current_longitude = current_longitude
        self.vehicle_status = vehicle_status  # 1 byte (Status flag 0-255)

        # Message attributes (default: no message)
        self.message_flag = message_flag  # 0 = No Message, 1 = Package, 2 = Patient
        self.message_lat = message_lat
        self.message_lon = message_lon
        self.patient_status = patient_status

    def encode(self):
        """Convert telemetry data into binary format."""
        
        # 6 floats, 1 Q, 2 doubles, 1 byte, 1 byte, 2 doubles = total 13 items
        format_string = "=6fQ2dBB2dB" 
        return struct.pack(format_string, 
                           self.speed, self.pitch, self.yaw, self.roll, 
                           self.altitude, self.battery_life, self.last_updated,
                           self.current_latitude, self.current_longitude, 
                           self.vehicle_status,
                           self.message_flag,  # Indicates whether a message is included
                           self.message_lat, self.message_lon, self.patient_status)

    @staticmethod
    def decode(binary_data):
        """Decode binary telemetry data into a Telemetry object."""
        expected_size = 67  # Total size of the telemetry packet (in bytes)
        if len(binary_data) != expected_size:
            print(f"Invalid telemetry packet size. Expected {expected_size}, got {len(binary_data)}")
            return None

        format_string = "=6fQ2dBB2dB"
        unpacked_data = struct.unpack(format_string, binary_data)

        return Telemetry(*unpacked_data)

    def __str__(self):
        message_info = (f"Message Type={self.message_flag}, "
                        f"Message Location=({self.message_lat}, {self.message_lon})") if self.message_flag else "No Message"

        return (f"Telemetry(Speed={self.speed}, Pitch={self.pitch}, Yaw={self.yaw}, Roll={self.roll}, "
                f"Altitude={self.altitude}, Battery Life={self.battery_life}, Last Updated={self.last_updated}, "
                f"Current Position=({self.current_latitude}, {self.current_longitude}), "
                f"Vehicle Status={self.vehicle_status}, {message_info}),"
                f"Patient Status = {self.patient_status}")