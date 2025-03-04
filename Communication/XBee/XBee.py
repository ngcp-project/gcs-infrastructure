import re
import serial
import time
from Communication.interfaces.Serial import Serial
from Logger.Logger import Logger
# import multiprocessing

class XBee(Serial):
    # Initialize serial connection
    def __init__(self, port: str, baudrate: int = 115200, status: bool = False, logger: Logger = None, config_file: str = None):
        """Initialize serial connection

        Args:
          port: Port of serial device.
          baudrate: Baudrate of serial device (/port)
          status: Automatically receive status packets after a transmission.
          logger: Logger instance
        """
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.status = status
        if logger is None:
            self.logger = Logger()
            self.logger.write("LOGGER CREATED By XBee.py")
        else:
            self.logger = logger
        self.timeout = 0.025 # Allow programmer to configure timeout?
        self.frame_id = 0x01

        self.config_file = config_file # Add AT_Config.py file

        self.__transmitting = False
        self.__receiving = False
    

    def open(self):
        """Opens serial port.

        Returns:
          True if success, False if failure.
        """
        self.logger.write("Attempting to open serial XBee connection.")
        
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0)
            
            self.logger.write("Serial port opened.")
            if self.config_file is not None:
                self.read_config(self.config_file)
        
        except serial.SerialException as e:
            self.logger.write((f"Error opening serial port: {e}"))
            print(f"Error opening serial port: {e}")
            return False
        
        return True
    

    def close(self):
        """Close serial port.

        Returns:
          True if success, False if failure (Error or port already closed).
        """
        if self.ser is not None:

            self.logger.write("Attempting to close serial XBee connection.")

            try:
                self.ser.close()
                
                self.logger.write("Serial port closed.")

                self.ser = None
            except Exception as e:
                self.logger.write(f"Error closing serial port: {e}")
            return True
        self.logger.write("Serial port is already closed.")
        return False


    def transmit_data(self, data, address = "0000000000000000", retrieveStatus = False) -> bool:
        """Transmit data.
        Args:
          data: String data to transmit.
          address: Address of destination XBee module. "0000000000000000" if no value is provided.

        Returns:
          True if success, False if failure.
        """
        if self.ser is not None:
            self.__transmitting = True
            self.logger.write(f"Transmitting data: {data} to {address}")
            self.ser.write(self.__encode_data(data, address))
            self.__transmitting = False

            # If retrieve status is true
            if(retrieveStatus):
                self.__receiving = True
                return self.__retrieve_status()
            # Return true once data is send to the XBee module over serial.
            # NOTE: This does not mean that a transmission is successful
            else:
                return 
        
        return False


    def retrieve_data(self):
        """
        Read incoming data in API mode:
        - Start delimiter (0x7E)
        - 2-byte Length
        - Frame Data (length bytes)
        - 1-byte Checksum

        Returns:
        - 0x81: 
        - 0x88: (frame_type, frame_id, at_command, command_status, command_data)
        - 0x89: 
        """

        # 1) Read one byte
        start_delim = self.ser.read(1)
        if not start_delim:
            # No data at all
            # print("NO START DELIM")
            return None
    
        self.logger.write("Receiving data:")

        # 2) Check if it's 0x7E
        if start_delim[0] != 0x7E:
            # Not the start delimiter -> leftover byte from a second frame?
            print(f"Pass {start_delim[0]:02x}")
            self.logger.write(f"Pass {start_delim[0]:02x}", self.logger.WARNING)
            return None

        # 3) Read the next 2 bytes for length
        length_bytes = self.ser.read(2)
        if len(length_bytes) < 2:
            # Not enough data
            self.logger.write(f"Pass. Unable to read length bytes", self.logger.WARNING)
            return None

        length = (length_bytes[0] << 8) + length_bytes[1]
        # print("\nLength bytes:", f"{length_bytes[0]:02x}", f"{length_bytes[1]:02x}")
        # print("Length:", length)

        # 4) Read 'length' bytes of frame data
        frame_data = b''
        frame_data += self.ser.read(length)
        timeout_start = time.time()
        while len(frame_data) < length and time.time() < timeout_start + self.timeout:
            time.sleep(0.001)
            chunk = self.ser.read(length - len(frame_data))
            frame_data += chunk


        # print("Data Between Length & Checksum Fields:")
        print(" ".join(f"{b:02x}" for b in frame_data))
        self.logger.write(" ".join(f"{b:02x}" for b in frame_data))

        # 5) Read the 1-byte checksum
        checksum_raw = self.ser.read(1)
        # print("DEBUG: checksum_raw =", checksum_raw)

        if len(checksum_raw) < 1:
            print("DEBUG: No checksum byte read!")
            self.logger.write(f"Pass. No checksum byte read!", self.logger.WARNING)
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
            self.logger.write(f"Checksum mismatch - ignoring frame: {frame_data} expected: {expected_checksum} received: {calculated_checksum}", self.logger.WARNING)
            return None

        # 8) Now parse the frame
        #    The first byte of frame_data is the frame_type
        frame_type = frame_data[0]
        if frame_type == 0x81:
            return self.__0x81(frame_data)
        
        elif frame_type == 0x88:
            return self.__0x88(frame_data)
        
        elif frame_type == 0x89:
            return self.__0x89(frame_data)
        
        else:
            # For all other frame types (e.g. 0x89 = TX Status), just ignore or print a debug
            self.logger.write(f"Pass. Unhandled frame type: {frame_data}", self.logger.ERROR)
            print(f"Got frame type: 0x{frame_type:02X}, ignoring.")
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
        frame.append(self.frame_id)  # Frame ID (1 bytes)
        self.frame_id = self.frame_id % 0xff + 0x01

        for i in range(8):  # 64-bit address (8 bytes)
            frame.append(int(address[2 * i : 2 * i + 2], 16))

        frame.append(0x00)  # Options (1 byte)
        frame.extend(data.encode('utf-8'))  # RF data (0 - 256 bytes)
        # FF - number of bytes between length & checksum field
        checksum = 0xFF - (sum(frame[3:]) & 0xFF)
        frame.append(checksum)  # Checksum (1 byte)

        # print(frame)
        print("Encoded data: " + ''.join('{:02x} '.format(x) for x in frame))
        self.logger.write("Encoded data: " + ''.join('{:02x} '.format(x) for x in frame))

        return frame
    
    def request_at_command_data(self, id):
        frame = bytearray()
        frame.append(0x7E) # Start delimiter (1 byte)
        frame.append(0x00) # Length (2 bytes)
        frame.append(0x04) # Length
        frame.append(0x08) # Frame Type (1 byte)
        frame.append(self.frame_id) # Frame ID (1 byte)
        self.frame_id = self.frame_id % 0xff + 0x01
        frame.extend(id.encode('utf-8')) # AT command (2 bytes)
        checksum = 0xFF - (sum(frame[3:]) & 0xFF)
        frame.append(checksum)  # Checksum (1 byte)

        print("Sending: " + ''.join('{:02x} '.format(x) for x in frame))
        self.logger.write("Sending: " + ''.join('{:02x} '.format(x) for x in frame))

        self.ser.write(frame)

        timeout_start = time.time()
        while time.time() < timeout_start + self.timeout:
            time.sleep(0.001)
            response = self.retrieve_data()

            if response is not None and response[0] == 0x88:
                self.logger.write(f"Response: {response}")
                return response
            
        self.logger.write("No response")
        return None

        # If retrieve status is true
        # if(retrieveStatus):
        # self.__receiving = True
        # return self.retrieve_data()
        # Return true once data is send to the XBee module over serial.
        # NOTE: This does not mean that a transmission is successful
        # else:
        #     return 

    def __0x81(self, frame_data):
        """Handle XBee Frame Type 81 (Frame Receive: 16-bit Address)

        Args:
          frame_data: Received bytes (between length and checksum fields)

        Returns:
          xxxxDecoded message & Received Signal Strength Indicator (RSSI), None if there is an error decoding message
          Returns 0x81 class (frame_type, frame_id, payload, rssi, ...)
        """
        rssi = -frame_data[3]
        payload = frame_data[5:]
        try:
            decoded_message = payload.decode()
            self.logger.write(f"Received payload. RSSI: {rssi}, Decoded message: {decoded_message}")
            print(f"RSSI (Signal Strength : {rssi} dBm)")
            print("Decoded message:", decoded_message)
            #print("RSSI:", rssi)    
            return decoded_message, rssi
        except UnicodeDecodeError:
            self.logger.write(f"Error decoding payload. RSSI: {rssi}, Decoded message: {decoded_message}")
            print("Error decoding payload")
            return None
        
    def __0x88(self, frame_data):
        """Handle XBee Frame Type 88 (AT Command Response)

        Args:
          frame_data: Received bytes (between length and checksum fields)

        Returns:
          Returns 0x88 class (frame_type, frame_id, at_command, command_status_ command_data)
        """
        # print(" ".join(f"{b:02x}" for b in frame_data))
        # print(frame_data)
        frame_type = frame_data[0]
        frame_id = frame_data[1]
        at_command = frame_data[2:4]
        command_status = frame_data[4]
        command_data = frame_data[5:]
        return frame_type, frame_id, at_command, command_status, command_data

    def __0x89(self, frame_data):
        """Handle XBee Frame Type 89 (Transmit Status)

        Args:
          frame_data: Received bytes (between length and checksum fields)

        Returns:
          xxxxDelivery ID & status of transmitted message
          Returns 0x89 class (frame_type, frame_id, ...)
        """
        id = frame_data[1]
        status = frame_data[2]
        self.logger.write(f"Transmit status. ID: {id}, Status: {status}")
        return id, status
    
    def read_config(self, filename):
        """
        Reads AT Commands from a file and logs their execution.
        """
        with open(filename, 'r') as file:
            lines = file.readlines()
        
        current_category = ""
        start_time = time.time()

        for line in lines:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                if line.startswith("#"):
                    current_category = line[1:].strip()
                    # print(f"\n{current_category}")
                    self.logger.write(f"\n{current_category}")
                continue
            
            # Subcategories (##)
            if line.startswith("##"):
                current_category = line[2:].strip()
                # print(f"\n{current_category}")
                self.logger.write(f"\n{current_category}")
                continue
            
            # Match AT Commands (handling special characters like % and ?)
            match = re.match(r"\*\s+([%A-Za-z0-9?]+)\s+-\s+(.+)", line)
            if match:
                at_command_id, command_name = match.groups()
                self.logger.write(f"Requesting: {at_command_id}")
                response = self.request_at_command_data(at_command_id)
                
                if response:
                    # if at_command_id
                    log_entry = f"{response}"
                    # print(f"Response: {log_entry}")
                    # self.logger.write(f"Response: {log_entry}")
                # else:
                    # print("No response")
                    # self.logger.write("No Response")
        end_time = time.time()
        self.logger.write(f"Retrieved config in: {end_time - start_time}s")
