import serial
import threading
import time
from Commands.RabbitMQ import CommandsRabbitMQ
from Types.CommandsEnum import CommandsEnum

PORT = "/dev/cu.usbserial-D30DWZL4" # Replace with your actual serial port. Plug in module and run "ls -l /dev/cu.usb*"
BAUD_RATE = 115200

transmit = False
transmit_lock = threading.Lock()

def transmit_data(ser, message):
    # Max message length is 256 bytes
    if(len(message) > 256):
        global transmit
        with transmit_lock:
            transmit = False
        return False

    print("Sending data...")
    message = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    frame = bytearray()
    frame.append(0x7E)  # Start delimiter
    frame.append(((len(message) + 11) // 256))  # Length
    frame.append((len(message) + 11) % 256)
    frame.append(0x00)  # Frame type
    frame.append(0x01)  # 64-bit address
    frame.append(0x00)  
    frame.append(0x00)  
    frame.append(0x00) 
    frame.append(0x00)  
    frame.append(0x00)  
    frame.append(0x00)  
    frame.append(0x00)  
    frame.append(0x00)  
    frame.append(0x00)  # Options
    frame.extend(message.encode('utf-8'))  # RF data
    checksum = 0xFF - (sum(frame[3:]) & 0xFF)
    frame.append(checksum)  # Checksum

    print(frame)

    ser.write(frame)

    global transmit
    with transmit_lock:
        transmit = False
    # time.sleep(0.1);
    print("Data sent!")
    return True

def frame_data(message, address=00000000):
    frame = bytearray()
    frame.append(0x7E)  # Start delimiter (1 byte)
    frame.append(((len(message) + 11) // 256))  # Length (2 bytes)
    frame.append((len(message) + 11) % 256)
    frame.append(0x00)  # Frame type (1 byte)
    frame.append(0x01)  # 64-bit address (8 bytes)
    for i in range(8):
        frame.append(address[i])
    frame.append(0x00)  # Options (1 byte)
    frame.extend(message.encode('utf-8'))  # RF data (0 - 256 bytes)
    checksum = 0xFF - (sum(frame[3:]) & 0xFF)
    frame.append(checksum)  # Checksum (1 byte)

    return frame

def deframe_data(frame):
    message = frame[15:-1].decode('utf-8')
    return message

def open_serial():
    try:
        # Open the serial port
        ser = serial.Serial(PORT, BAUD_RATE, timeout=0)  # timeout is optional

        print(f"Connected to {PORT} at {BAUD_RATE} baud.")

        while True:
            # Read a line of data from the serial port
            data = ser.readline()  # Read until a newline character
            global transmit
            if transmit == True:
                transmit_data(ser)
            if data:
                print(f"Received: {deframe_data(data)}")  
            

    except serial.SerialException as e:
        print(f"[*] Error: {e}")

    except KeyboardInterrupt:
        print("[*] Exiting...")

def callback_keepin(body):
        print("Target received from GCS!")
        global transmit

        with transmit_lock:
            transmit = True
        print(body)

def open_rabbitmq():
    vehicle = CommandsRabbitMQ("ERU")                   

    try:
        vehicle.subscribe(CommandsEnum.KEEP_IN, callback_keepin)
        vehicle.start_connection()

    except KeyboardInterrupt:
        print("[*] Exiting...")
        vehicle.close_connection()

def main():
    # Thread for serial communication
    t1 = threading.Thread(target=open_serial)

    # Thread for RabbitMQ communication
    t2 = threading.Thread(target=open_rabbitmq)
    
    t1.start()
    t2.start()

    t1.join()
    t2.join()

if __name__ == '__main__':
    main()