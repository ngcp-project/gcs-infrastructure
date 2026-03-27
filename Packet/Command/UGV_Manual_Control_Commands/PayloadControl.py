from Interfaces.CommandInterface import CommandInterface
import struct

class PayloadControl(CommandInterface):
    FORMAT_STRING = "BBb"
    PAYLOAD_ID = 1 # All commands will have a payload ID of 1
    COMMAND_ID = 8

    @staticmethod
    def encode_packet(payload_direction) -> bytes:
        """Encode data packet

        Args:
            payload_direction: Direction of payload movement. -1 for down, 1 for up

        Returns:
            Encoded data bytes
        """
        encoded_string = struct.pack(PayloadControl.FORMAT_STRING, PayloadControl.PAYLOAD_ID,
                                     PayloadControl.COMMAND_ID, payload_direction)
        return encoded_string

    @staticmethod
    def decode_packet(encoded_string) -> int:
        """Decodes data packet
        
        Args:
            encoded_string: Encoded data packet

        Returns:
            Data from encoded data packet
        """
        expected_size = 3
        if len(encoded_string) != expected_size:
            print("Invalid String Size")
        unpacked_data = struct.unpack(PayloadControl.FORMAT_STRING, encoded_string)

        return unpacked_data[2]