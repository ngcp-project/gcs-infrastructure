from digi.xbee.devices import XBeeDevice

PORT = "COM1"
BAUD_RATE = 9600


def main():
    device = XBeeDevice(PORT, BAUD_RATE)

    try:
        device.open()

        device.flush_queues()

        print("Waiting for data...\n")

        while True:
            xbee_message = device.read_data()
            if xbee_message is not None:
                print("From %s >> %s" % (xbee_message.remote_device.get_64bit_addr(),
                                         xbee_message.data.decode()))

    finally:
        if device is not None and device.is_open():
            device.close()


if __name__ == '__main__':
    main()