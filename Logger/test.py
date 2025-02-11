# import Logger

# logger = Logger.Logger()


# logger.write("test")
# opened = True
# logger.write(f"Opening XBee connection... {"Success" if opened else "Failed"}")
# opened = False
# logger.write(f"Opening XBee connection... {"Success" if opened else "Failed"}")
# # print(logger.test())

data = "hello"
address = "0013A20042435EA9"
frame = bytearray()
# frame.append(0x7E)  # Start delimiter (1 byte)
# frame.append(((len(data) + 11) // 256))  # Length (2 bytes)
# frame.append((len(data) + 11) % 256)
# frame.append(0x00)  # Frame type (1 byte)
# frame.append(0x01)  # Frame ID (1 bytes)

for i in range(8):  # 64-bit address (8 bytes)
    frame.append(int(address[2*i:2*i+2], 16))

print(''.join('{:02x} '.format(x) for x in frame))