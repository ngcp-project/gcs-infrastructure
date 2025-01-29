import serial
from Communication.interfaces.Serial import Serial
# import multiprocessing

class XBee(Serial):
    # Initialize serial connection
    def __init__(self, port, baudrate = 9600):
        """Initialize serial connection

        Args:
          port: Port of serial device.
          baudrate: Baudrate of serial device.
        """
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.__transmitting = False
        self.__receiving = False
    

    def open(self):
        """Opens serial port.

        Returns:
          True if success, False if failure.
        """
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0)
        except serial.SerialException:
            print("Error opening serial port")
            return False
        
        return True
    

    def close(self):
        """Close serial port.

        Returns:
          True if success, False if failure (Error or port already closed).
        """
        if self.ser is not None:
            self.ser.close()
            self.ser = None
            return True
        return False


    def transmit_data(self, data, address = "0000000000000000"):
        """Transmit data.
        Args:
          data: String data to transmit.
          address: Address of destination XBee module. "0000000000000000" if no value is provided.

        Returns:
          True if success, False if failure.
        """
        if self.ser is not None:
            self.__transmitting = True
            self.ser.write(self.__encode_data(data, address))
            self.__transmitting = False
            return True
        return False


    def retrieve_data(self):
        """Read incomming data.

        Returns:
          Incomming String data (Deframed data), None if no data.
        """
        # bytes = self.ser.readline()

        # if bytes:
        #   print(''.join('{:02x} '.format(x) for x in bytes))

        byte = self.ser.read(1)

        # Read byte by byte until start delimiter (7E) is read
        if byte and byte[0] == 0x7E:
            # # print(hex(byte[0]))
            # print('{:02x} '.format(byte[0]))
            self.__receiving = True
            # # It might be possible for nothing to be read, leading to an incorrect length
            l1 = self.ser.read(1)
            l2 = self.ser.read(1)
            print("Length bytes:",'{:02x} '.format(l1[0]),'{:02x} '.format(l2[0]))
            length = l1[0] * 256 + l2[0]
            print("Length:", length)
            data = b''
            while len(data) < length:
                chunk = self.ser.read(length - len(data))
                data += chunk
            print("Data Between Length & Checksum Fields:")
            # for b in data:
            #     print('{:02x} '.format(b))
            #     # print("Data:", data)
            print(''.join('{:02x} '.format(x) for x in data))
            while True:
                expected_checksum = self.ser.read(1)
                if expected_checksum:
                    print("Received Checksum:", '{:02x} '.format(expected_checksum[0]))
                    calculated_checksum = 0xFF - (sum(data) & 0xFF)
                    print("Calculated Checksum:", '%0.2x' % calculated_checksum)
                    if expected_checksum[0] == calculated_checksum:
                        return data[5:].decode()
                    break
            # return self.__decode_data()
        elif byte:
        #     print(data, data[0])
        #     print(data[0] == 0x7E)
        #     print("Incomming framed data:")
            # print(byte)
            print('Pass {:02x} '.format(byte[0]))
        #     data = self.__decode_data(data)
            # print("Decoded data:" + data)
            # return data
        return None
    

    # NOTE** Might need to check data length
    def __encode_data(self, data, address = "0000000000000000"):
        """Encode String data.

        Args: 
          data: String data to encode.
          address: Address of destination XBee module. "0000000000000000" if no value is provided.
        Returns:
          Framed String data.
        """
        frame = bytearray()
        frame.append(0x7E)  # Start delimiter (1 byte)
        frame.append(((len(data) + 11) // 256))  # Length (2 bytes)
        frame.append((len(data) + 11) % 256)
        frame.append(0x00)  # Frame type (1 byte)
        frame.append(0x01)  # Frame ID (1 bytes)

        for i in range(8):  # 64-bit address (8 bytes)
            frame.append(int(address[2 * i : 2 * i + 2], 16))

        frame.append(0x00)  # Options (1 byte)
        frame.extend(data.encode('utf-8'))  # RF data (0 - 256 bytes)
        # FF - number of bytes between length & checksum field
        checksum = 0xFF - (sum(frame[3:]) & 0xFF)
        frame.append(checksum)  # Checksum (1 byte)

        # print(frame)
        print(''.join('{:02x} '.format(x) for x in frame))

        return frame
    
    # Frames may be sent separately (different lines)
    # https://pyserial.readthedocs.io/en/latest/pyserial_api.html
    # 1. Read byte by byte until 7E (~) is read. -> read(1)
    # 2. Read next 2 bytes to determine frame size (length) -> read(2)
    # 3. Read next "length" bytes -> read(length)
    # 4. Read final byte for checksum-> read(1)
    # NOTE** Might be able to use read_until(exptected, size) https://pyserial.readthedocs.io/en/latest/pyserial_api.html#serial.Serial.read_until
    # 5. Check if calculated checksum is equal to the read checksum value
    # def __decode_data(self, data): 
    #     """Decode String data.

    #     Args: 
    #       data: String data to decode.

    #     Returns:
    #       Deframed String data.
    #     """
    #     # print("data: ", data[1])
    #     print(data[1], data[2])
    #     length = (data[1] * 256) + data[2]
    #     print("Length:", length)
    #     # for byte in data:
    #     #     print(byte)
    #     message = data[15:-1].decode('utf-8')
    #     return message
