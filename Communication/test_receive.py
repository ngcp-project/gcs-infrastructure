from digi.xbee.devices import XBeeDevice

PORT = "COM1"
BAUD_RATE = 9600

def main():
    device = XBeeDevice(PORT, BAUD_RATE)

    try:
        device.open()

        def data_receive_callback(xbee_message):
            print("From %s >> %s" % (xbee_message.remote_device.get_64bit_addr(), xbee_message.data.decode()))

        device.add_data_received_callback(data_receive_callback)

        print("Waiting for data...\n")
        input()
    
    finally:
        if device is not None and device.is_open():
            device.close()

if __name__ == '__main__':
    main()