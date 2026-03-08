from Interfaces.CommandInterface import CommandInterface
import struct



class VelocityControl(CommandInterface):


    FORMAT_STRING = "BBb"


    PAYLOAD_ID = 1 # All commands will have a payload ID of 1


    COMMAND_ID = 7



    @staticmethod


    def encode_packet(turn_angle) -> bytes:


        """Encode data packet



         Args:


            velocity: Value from -100 to 100 representing turn angle of the wheels. 


            Negative for left and positive for right.



        Returns:


            Encoded data bytes
        """



        encoded_string = struct.pack(VelocityControl.FORMAT_STRING, VelocityControl.PAYLOAD_ID, 

                                     VelocityControl.COMMAND_ID, turn_angle)
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


        unpacked_data = struct.unpack(VelocityControl.FORMAT_STRING, encoded_string)


        return unpacked_data[2]