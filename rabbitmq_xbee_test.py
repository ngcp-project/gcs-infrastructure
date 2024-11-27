import serial
import threading
from Commands.RabbitMQ import CommandsRabbitMQ
from Types.CommandsEnum import CommandsEnum

PORT = "/dev/cu.usbserial-D30DWZKT"
BAUD_RATE = 115200

transmit = False
transmit_lock = threading.Lock()

def transmit_data(ser):
    global transmit
    with transmit_lock:
        transmit = False
    print("Sending data...")
    ser.write(b"Hello XBee")

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
                print(f"Received: {data}")  # Decode and strip newlines
            

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
    t1 = threading.Thread(target=open_serial)
    t2 = threading.Thread(target=open_rabbitmq)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

if __name__ == '__main__':
    main()