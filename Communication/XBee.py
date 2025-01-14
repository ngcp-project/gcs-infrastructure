import serial
# import multiprocessing

class XBee:
    # Initialize serial connection
    def __init__(self, port, baudrate):
        """Initialize serial connection

        Args:
          port: Port of serial device.
          baudrate: Baudrate of serial device.
        """
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.__transmitting = False
    

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
            self.ser.write(self.__encode_data(data, address))
            return True
        return False


    def receive_data(self):
        """Read incomming data.

        Returns:
          Incomming String data, None if no data.
        """
        data = self.ser.readline()
        if data == None:
            return None
        data = self.__decode_data(data)
        return data
    

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
        checksum = 0xFF - (sum(frame[3:]) & 0xFF)
        frame.append(checksum)  # Checksum (1 byte)

        print(frame)

        return frame
    

    def __decode_data(self, data): # NOTE** Might need to retrieve sender address
        """Decode String data.

        Args: 
          data: String data to decode.

        Returns:
          Deframed String data.
        """
        message = data[15:-1].decode('utf-8')
        return message

    # # Read next incoming data (Include timeout?)
    # def read_next(self):
    #     try:
    #         while True:
    #             data = self.receive_data()
    #             if data:
    #                 # print(f"Received data: {data}")
    #                 return data

    #     except serial.SerialException as e:
    #         print(f"Error: {e}")
    #         return False
