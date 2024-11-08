from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress

PORT = "/dev/cu.usbserial-D30DWZKT"  # Replace with your actual serial port. Plug in module and run "ls -l /dev/cu.usb*"
BAUD_RATE = 9600

def data_receive_callback(xbee_message):
    print("From %s >> %s" % (xbee_message.remote_device.get_64bit_addr(), xbee_message.data.decode()))

def main():
    xbee = XBeeDevice(PORT, BAUD_RATE)
    remote = RemoteXBeeDevice(xbee, XBee64BitAddress.from_hex_string("0013A20042435A3D")) # Replace with remote device's 64-bit address (MAC address)

    try:
        xbee.open()
        print(xbee.get_64bit_addr())

        # data_to_send = input()
        # print("Sending broadcast data: %s..." % "data_to_send")

        # xbee.send_data_broadcast("data_to_send")
        # xbee.send_data_async(remote, "Hello XBee!")

        print("xbee opened")

        xbee.add_data_received_callback(data_receive_callback)

        # print("Waiting for data...\n")
    except Exception as e:
        print(f"Error: {e}")
        
    while xbee is not None and xbee.is_open():
        try:
                data_to_send = input()
                print("Sending broadcast data: %s..." % data_to_send)

                # xbee.send_data_broadcast(data_to_send)
                # xbee.send_data_async(remote, data_to_send)
                xbee.send_data(remote, data_to_send)
                print("Data sent")
        
        except Exception as e:
            print(f"Error: {e}")

    # finally:
    #     if xbee is not None and xbee.is_open():
    #         xbee.close()

if __name__ == '__main__':
    main()