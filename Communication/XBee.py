import serial
# import multiprocessing

class XBee:
    # Initialize serial connection
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.__transmitting = False
    
    # Open serial connection
    def open(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0)
        except serial.SerialException:
            print("Error opening serial port")
            return False
        
        return True
    
    # Close serial connection
    def close(self):
        self.ser.close()
        self.ser = None

    # Transmit data
    def transmit_data(self, data, address = "00000000"):
        self.ser.write(self.encode_data(data, address))

    # Receive data
    def receive_data(self):
        data = self.ser.readline()
        if data == None:
            return None
        data = self.decode_data(data)
        return data
    
    # Encode data
    # NOTE** Might need to check data length
    def encode_data(self, data, address = "00000000"):
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
    
    # Decode data
    def decode_data(self, data): # NOTE** Might need to retrieve sender address
        message = data[15:-1].decode('utf-8')
        return message

    # Read next incoming data (Include timeout?)
    def read_next(self):
        try:
            while True:
                data = self.receive_data()
                if data:
                    # print(f"Received data: {data}")
                    return data

        except serial.SerialException as e:
            print(f"Error: {e}")
            return False
