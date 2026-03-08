from Interfaces.CommandInterface import CommandInterface
import struct

class PayloadControl(CommandInterface):
    FORMAT_STRING = "BBB"
    PAYLOAD_ID = 1 # All commands will have a payload ID of 1
    COMMAND_ID = 8

    @staticmethod
    def encode_packet(payload_status) -> bytes:
        """Encode data packet

        Args:
            payload_status: Status for payload position: 0 = Lower Payload, 1 = Raise Payload

        Returns:
            Encoded data bytes
        """
        encoded_string = struct.pack(PayloadControl.FORMAT_STRING, PayloadControl.PAYLOAD_ID,
                                     PayloadControl.COMMAND_ID, payload_status)
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