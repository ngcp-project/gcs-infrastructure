from Interfaces.CommandInterface import CommandInterface

import struct
import json

class PatientLocation(CommandInterface):
    PAYLOAD = 1 # All commands will have a payload ID of 1
    COMMAND_ID = 5

    @staticmethod
    def encode_packet(coordinates) -> bytes:
        """Encode data packet

        Args:
            coordinates: List of (x, y) tuples to encode as doubles

        Returns:
            Encoded data bytes
        """

        # Packet header "B" = unsigned byte, two of them are there to represent the two arguements added, if we added another argument it would be BBB
        header_byte_struct = "BB"
        header = struct.pack(header_byte_struct, PatientLocation.PAYLOAD_ID, PatientLocation.COMMAND_ID)

        # Turn the tuples into a list
        coordinate_list = []
        for coord in coordinates:
            for item in coord:
                coordinate_list.append(item)
        print(f"coords: {coordinate_list}")

        
        if coordinate_list:
            coord_byte_struct = f"{len(coordinate_list)}d"
            coord_byte_stream = struct.pack(coord_byte_struct, *coordinate_list)
            encoded_stream = header + coord_byte_stream
        else:
            encoded_stream = header
        return encoded_stream
    
    
    def decode_packet(encoded_string) -> list:
        """Decodes data packet
        
        Args:
            encoded_string: Encoded data packet

        Returns:
            List of (x, y) coordinate tuples
        """

        num_coordinates = (len(encoded_string) - 2) // 16
        decode_byte_struct = "=BB" + "dd" * int(num_coordinates)

        print(f"byte structure: {decode_byte_struct}")

        expected_length = struct.calcsize(decode_byte_struct)
        if len(encoded_string) != expected_length:
            raise ValueError(f"Encoded string length {len(encoded_string)}")
        
        unpacked_data = struct.unpack(decode_byte_struct, encoded_string)

        # we are ignoring the "=BB" part here
        coords = unpacked_data[2:]
        return [(coords[i], coords[i+1]) for i in range(0, len(coords), 2)]
        


    @staticmethod
    def to_json(encoded_string) -> str:
        """Decodes data packet and returns JSON string with coordinate tuples

        Args:
            encoded_string: Encoded data packet

        Returns:
            JSON string with coordinates
        """

        coordinates = PatientLocation.decode_packet(encoded_string)
        # Convert list of tuples to list of dictionaries with lat/lon keys
        json_coords = [{"lat": lat, "lon": lon} for lat, lon in coordinates]
        return json.dumps(json_coords, indent=2)
    
