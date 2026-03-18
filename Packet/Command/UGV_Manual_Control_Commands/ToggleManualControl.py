from Interfaces.CommandInterface import CommandInterface
import struct


class ToggleManualControl(CommandInterface):

    FORMAT_STRING = "BBB"
    PAYLOAD_ID = 1;
    COMMAND_ID = 5;

    @staticmethod
    def encode_packet(manual_status) -> bytes:
        """Encode data packet
        Args:
            manual_status: Status for manual control: 0 = Enable manual control, 1 = Disable manual control
       
        Returns:
            Encoded data bytes
        """


        encoded_string = struct.pack(ToggleManualControl.FORMAT_STRING, ToggleManualControl.PAYLOAD_ID, 
                                     ToggleManualControl.COMMAND_ID, manual_status)
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
        unpacked_data = struct.unpack(ToggleManualControl.FORMAT_STRING, encoded_string)

        return unpacked_data[2]