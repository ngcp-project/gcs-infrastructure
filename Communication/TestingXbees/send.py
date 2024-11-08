from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress

# Replace with the GCS's port and baud rate
PORT = "/dev/cu.usbserial-D30DWZKY"  # Adjust based on your setup
BAUD_RATE = 9600

# Replace with the 64-bit addresses of the vehicle Xbees
VEHICLE_0_ADDRESS = "0013A20040XXXXXX"  
VEHICLE_1_ADDRESS = "0013A20040YYYYYY"  

def main():
    device = XBeeDevice(PORT, BAUD_RATE)
    
    try:
        device.open()
        
        # Define remote devices for vehicle0 and vehicle1
       # vehicle0 = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string())
        vehicle1 = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string("0013A200424366C"))


        #Sending "Hello" message to vehicle0
        print("Sending 'Hello' to vehicle0...")
        device.send_data(vehicle0, "Hello from GCS to vehicle0")
        print("Message sent to vehicle0!")

        # Sending "Hello" message to vehicle1
        print("Sending 'Hello' to vehicle1...")
        device.send_data(vehicle1, "Hello from GCS to vehicle1")
        print("Message sent to vehicle1!")
        
        # Listening for responses
        print("Waiting for responses from vehicles...\n")
        
        def data_receive_callback(xbee_message):
            print("Received data from {}: {}".format(
                xbee_message.remote_device.get_64bit_addr(),
                xbee_message.data.decode()
            ))

        # Register the callback for incoming data
        device.add_data_received_callback(data_receive_callback)
        
        input("Press Enter to stop listening...\n")
        
    finally:
        if device is not None and device.is_open():
            device.close()

if __name__ == '__main__':
    main()
