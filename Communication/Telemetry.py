import struct

class Telemetry:
    """Handles telemetry data encoding and decoding for UAV/UGV communication."""
    
    def __init__(self, speed, pitch, yaw, roll, altitude, battery_life, last_updated, 
                 current_latitude, current_longitude, vehicle_status, 
                 patient_latitude, patient_longitude):
        self.speed = speed
        self.pitch = pitch
        self.yaw = yaw
        self.roll = roll
        self.altitude = altitude
        self.battery_life = battery_life
        self.last_updated = last_updated  # Timestamp (8 bytes)
        self.current_latitude = current_latitude
        self.current_longitude = current_longitude
        self.vehicle_status = vehicle_status  # 1 byte
        self.patient_latitude = patient_latitude
        self.patient_longitude = patient_longitude

    def encode(self):
        """Convert telemetry data into binary format using single precision (4-byte floats)."""
        format_string = "7fQ2fB2f"  # 7 floats, 1 uint64 (Q), 2 floats, 1 byte, 2 floats
        return struct.pack(format_string, 
                           self.speed, self.pitch, self.yaw, self.roll, 
                           self.altitude, self.battery_life, self.last_updated,
                           self.current_latitude, self.current_longitude, 
                           self.vehicle_status,
                           self.patient_latitude, self.patient_longitude)

    @staticmethod
    def decode(binary_data):
        """Decode binary telemetry data into a Telemetry object using single precision."""
        expected_size = 53  # Total size of the telemetry packet (in bytes)
        if len(binary_data) != expected_size:
            print(f"Invalid telemetry packet size. Expected {expected_size}, got {len(binary_data)}")
            return None

        format_string = "7fQ2fB2f"
        unpacked_data = struct.unpack(format_string, binary_data)

        return Telemetry(*unpacked_data)

    def __str__(self):
        return (f"Telemetry(Speed={self.speed}, Pitch={self.pitch}, Yaw={self.yaw}, Roll={self.roll}, "
                f"Altitude={self.altitude}, Battery Life={self.battery_life}, Last Updated={self.last_updated}, "
                f"Current Position=({self.current_latitude}, {self.current_longitude}), "
                f"Vehicle Status={self.vehicle_status}, "
                f"Patient Location=({self.patient_latitude}, {self.patient_longitude}))")

