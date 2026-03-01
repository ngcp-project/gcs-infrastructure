from Interfaces.CommandInterface import CommandInterface

import struct
import json
import warnings

class PatientLocation(CommandInterface):
    PAYLOAD = 1 # All commands will have a payload ID of 1
    COMMAND_ID = 5

    @staticmethod
    def encode_packet(coordinates: tuple) -> bytes:
        """Encode data packet

        Args:
            coordinates: single (x, y) tuple to encode as doubles

        Returns:
            Encoded data bytes
        """

        # how struct.pack and its format characters (e.g. "BB" or "dd") are explained here https://docs.python.org/3/library/struct.html 
        # encodes the header
        header_byte_struct = "BB"
        header = struct.pack(header_byte_struct, PatientLocation.PAYLOAD_ID, PatientLocation.COMMAND_ID)

        # encodes the byte stream coordinate data
        coord_byte_struct = "dd"
        coord_byte_stream = struct.pack(coord_byte_struct, coordinates[0], coordinates[1])

        encoded_stream = header + coord_byte_stream
    
        return encoded_stream
    
    
    @staticmethod
    def decode_packet(encoded_string, format: str = None):
        """Decodes data packet
        
        Args:
            encoded_string: Encoded data packet
            format: "tuple" or "json". Defaults to "tuple" with a warning if not provided.

        Returns:
            (x, y) tuple or JSON string with x and y keys
        """
        if format is None:
            warnings.warn("Format not specified in decode_packet, defaulting to 'tuple'", UserWarning)

        decode_byte_struct = "=BBdd"

        expected_length = struct.calcsize(decode_byte_struct)
        if len(encoded_string) != expected_length:
            raise ValueError(f"Encoded string length {len(encoded_string)} does not match expected length {expected_length}")
        
        unpacked_data = struct.unpack(decode_byte_struct, encoded_string)

        # we are ignoring the "=BB" part here which is the header, "unpacked_data" would look like [1, 5, <some double value>, <some double value>]
        x, y = unpacked_data[2], unpacked_data[3]
        
        if format == "json":
            return json.dumps({"x": x, "y": y}, indent=2)
        
        return (x, y)
        
    
