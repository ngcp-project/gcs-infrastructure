# from Interfaces.CommandInterface import CommandInterface
import struct

# class EmergencyStop(CommandInterface):
#     def __init__(self):
FORMAT_STRING = "BBB"
PAYLOAD_ID = 1 # All commands will have a payload ID of 1
COMMAND_ID = 1

def encode_emergency_stop(stop_status) -> str:
    """Encode data packet

    Args:
        stop_status: Status for emergency stop: 0 = Enable Emergency Stop, 1 = Disable Emergency Stop

    Returns:
        Encoded data string
    """
    encoded_string = struct.pack(FORMAT_STRING, PAYLOAD_ID, COMMAND_ID, stop_status)
    return encoded_string

def decode_emergency_stop(encoded_string) -> str:
    """Decodes data packet
    
    Args:
        Encoded data packet

    Returns:
        Data from encoded data packet
    """
    expected_size = 3
    if len(encoded_string) != expected_size:
        print("Invalid String Size")
    unpacked_data = struct.unpack(FORMAT_STRING, encoded_string)

    return unpacked_data[2]
