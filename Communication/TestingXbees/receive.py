from digi.xbee.devices import XBeeDevice

# Replace with each vehicle's specific port and baud rate
PORT = "/dev/tty.usbserial-D30DWZKY"  # Adjust based on your setup
BAUD_RATE = 9600

def main():
    device = XBeeDevice(PORT, BAUD_RATE)
    
    try:
        device.open()
        
        print("Waiting for messages from GCS...\n")
        
        def data_receive_callback(xbee_message):
            print("Received message from GCS: {}".format(xbee_message.data.decode()))
            
            # Send a response back to the GCS
            print("Sending response back to GCS...")
            device.send_data(xbee_message.remote_device, "Hello from Vehicle")
            print("Response sent to GCS!")
        
        # Register the callback for incoming data
        device.add_data_received_callback(data_receive_callback)
        
        input("Press Enter to stop listening...\n")
        
    finally:
        if device is not None and device.is_open():
            device.close()

if __name__ == '__main__':
    main()
