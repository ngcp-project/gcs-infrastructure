from digi.xbee.devices import XBeeDevice
import time

# TODO: Replace with the serial port where your local module is connected to.
# PORT = "/dev/cu.usbserial-D30DWZKT"
PORT = "/dev/cu.usbserial-D30DWZKT"
# TODO: Replace with the baud rate of your local module.
BAUD_RATE = 115200


def main():
    print(" +-------------------------------------------------+")
    print(" | XBee Python Library Receive Data Polling Sample |")
    print(" +-------------------------------------------------+\n")

    device = XBeeDevice(PORT, BAUD_RATE)

    try:
        device.open()

        device.flush_queues()

        print("Waiting for data...\n")
        end = 0
        while True:
            xbee_message = device.read_data()
            # if xbee_message is not None:
            #     start = time.time()
            #     print(end - start)
            #     end = time.time()
            #     print("From %s >> %s" % (xbee_message.remote_device.get_64bit_addr(),
            #                              xbee_message.data.decode()))
            # # print(a);
            # # a += 1
            # # device.flush_queues()
            try:
                if xbee_message is not None:
                    print(xbee_message)
            except:
                pass

    finally:
        if device is not None and device.is_open():
            device.close()


if __name__ == '__main__':
    main()