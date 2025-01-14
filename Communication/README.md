## XBee Frame (API Mode - Frame Type 00)

### Start delimiter (1 byte)
Always set to **7E** in XBee API Mode

### Length (2 bytes)
Number of bytes between Length and Checksum fields

### Frame type (1 byte)
Specefies XBee API frame type 

![XBee API frame types](./images/XBee%20API%20Frame%20Types.png)

### Frame ID (1 byte)
Identifies the UART data frame for the hose to match with subsequent reqponse. If 0, no response is requested

### 64-bit Destination Address (8 bytes)
Set to the 64-bit address of the destination XBee module. 
Use `00 00 00 00 00 00 FF FF` to send a broadcast packet.

### Options (1 byte)
![XBee API frame options](./images/XBee%20API%20Frame%20Options.png)

### RF data (0 - 256 bytes)
Packet payload, up to **256** bytes (256 characters)

### Checksum (1 byte)
FF minus 8-bit sum of bytes between length and checksum fields.

