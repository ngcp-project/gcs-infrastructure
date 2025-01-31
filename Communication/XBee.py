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


    def transmit_data(self, data, address = "00000000"):
        """Transmit data.

        Args:
          data: String data to transmit.
          address: Address of destination XBee module. "00000000" if no value is provided.

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
        """
        Read incoming data in API mode:
        - Start delimiter (0x7E)
        - 2-byte Length
        - Frame Data (length bytes)
        - 1-byte Checksum
        """

        # 1) Read one byte
        start_delim = self.ser.read(1)
        if not start_delim:
            # No data at all
            return None

        # 2) Check if it's 0x7E
        if start_delim[0] != 0x7E:
            # Not the start delimiter -> leftover byte from a second frame?
            print(f"Pass {start_delim[0]:02x}")
            return None

        # 3) Read the next 2 bytes for length
        length_bytes = self.ser.read(2)
        if len(length_bytes) < 2:
            # Not enough data
            return None

        length = (length_bytes[0] << 8) + length_bytes[1]
        print("\nLength bytes:", f"{length_bytes[0]:02x}", f"{length_bytes[1]:02x}")
        print("Length:", length)

        # 4) Read 'length' bytes of frame data
        frame_data = self.ser.read(length)
        if len(frame_data) < length:
            # Incomplete frame
            return None

        print("Data Between Length & Checksum Fields:")
        print(" ".join(f"{b:02x}" for b in frame_data))

        # 5) Read the 1-byte checksum
        checksum_raw = self.ser.read(1)
        print("DEBUG: checksum_raw =", checksum_raw)

        if len(checksum_raw) < 1:
            print("DEBUG: No checksum byte read!")
            # Did not get the checksum byte
            return None

        expected_checksum = checksum_raw[0]

        # 6) Calculate & print checksums
        calculated_checksum = 0xFF - (sum(frame_data) & 0xFF)
        print("Received Checksum:", f"{expected_checksum:02x}")
        print("Calculated Checksum:", f"{calculated_checksum:02x}")

        # 7) Compare checksums
        if expected_checksum != calculated_checksum:
            print("Checksum mismatch - ignoring frame.")
            return None

        # 8) Now parse the frame
        #    The first byte of frame_data is the frame_type
        frame_type = frame_data[0]

        if frame_type == 0x81:
            # 0x81 = Receive Packet (16-bit addr)
            # According to XBee docs:
            #   byte[0] = 0x81
            #   byte[1..2] = 16-bit source address
            #   byte[3] = RSSI
            #   byte[4] = Receive options
            #   byte[5..] = RF payload

            rssi = -frame_data[3]
            payload = frame_data[5:]
            try:
                decoded_message = payload.decode()
                print(f"RSSI (Signal Strength : {rssi} dBm)")
                print("Decoded message:", decoded_message)
                #print("RSSI:", rssi)    
                return decoded_message, rssi
            except UnicodeDecodeError:
                print("Error decoding payload")
                return None
        
        elif frame_type == 0x89:
            # TX status or something else, ignore
            print(f"Got frame type 0x89 - ignoring")
            return None

        else:
            # For all other frame types (e.g. 0x89 = TX Status), just ignore or print a debug
            print(f"Got frame type: 0x{frame_type:02X}, ignoring.")
            return None

    

    # NOTE** Might need to check data length
    def __encode_data(self, data, address = "00000000"):
        """Encode String data.

        Args: 
          data: String data to encode.
          address: Address of destination XBee module. "00000000" if no value is provided.

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
            frame.append(int(address[i], 16))

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
