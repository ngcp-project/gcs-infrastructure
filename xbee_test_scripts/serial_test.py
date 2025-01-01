from Communication.XBee import XBee

port = "/dev/cu.usbserial-D30DWZL4"

while True:
    # Initialize XBee object
    xbee = XBee(port, 9600)
    # Open serial connection
    try:
        xbee.open()
    except Exception as e:
        print(f"Error: {e}")

    while xbee is not None and xbee.ser is not None:
        try:
            data_to_send = input()
            print("Sending: %s..." % data_to_send)

            xbee.transmit_data(data_to_send)
            print("Data sent")
        
        except Exception as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            break
        finally:
            # Close serial connection
            print("Closing serial connection...")
            xbee.close()

    # Transmit data
    # xbee.transmit_data("Hello, world!")
    # Receive data
    print(xbee.receive_data())
    # Close serial connection
    xbee.close()