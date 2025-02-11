# XBee Serial Library

## Requirements
* Python 2.7 or Python 3.4 and newer
* pyserial 3.5

## Finding the serial port (device name)
### Mac
1. Plug in XBee RF module
2. Run `ls -l /dev/cu.usb*`
3. The device name should look similar to this:

`/dev/cu.usbserial-D30DWZKT`

### Linux

...

### Windows

...

## Constructor

`__init__(port, baudrate)`

Initializes serial port

**Parameters**

* *port* (str or None) - Port of serial device.
* *baudrate* (int) - Baudrate of serial device.

**Example**

```py
from Communication.XBee import XBee

PORT = "/dev/cu.usbserial-D30DWZKT"
BAUD_RATE = 115200
xbee = XBee(PORT, BAUD_RATE)
```

## Methods

`open()`

Open an XBee connection over the serial port.

**Returns:**
* *True* if success, *False* if failure.

**Throws:**
* *SerialException* - if there is an error opening the serial port

`close()`

Close an XBee connection over the serial port.

**Returns:**
* *True* if success, *False* if failure.

`transmit_data(string data, string address)`

Send data to another XBee module(s)

**Parameters:**

* *data* (str) -  String data to transmit.
* *address* (str) - Address of destination XBee module. "00000000" if no value is provided.

**Returns:**
* *True* if success, *False* if failure.

`retrieve_data()`

Check for incomming data

**Returns:**
* *String* if ther is incomming data. *None* otherwise.

# XBee Frame Information

## XBee Frame Transmit: 64-bit Address(API Mode - Frame Type 00)

### Start delimiter (1 byte)
Always set to **7E** in XBee API Mode

### Length (2 bytes)
Number of bytes between Length and Checksum fields

> [!Note]
> The maximum length should be `00 6F` or `111` bytes ([See RF data](#rf-data-0---256-bytes))

### Frame type (1 byte)
Specefies XBee API frame type (0x00)

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

> [!Important]
> Although it is stated that the packet payload can be 0 - 256 bytes, the packet payload can only be up to **100** bytes (100 characters)
>
![Xbee Maximum Packet Payload Length](./images/XBee%20Maximum%20Packet%20Payload%20Length.png)

### Checksum (1 byte)
FF minus 8-bit sum of bytes between length and checksum fields.

## XBee Frame Receive: 16-bit Address(API Mode - Frame Type 81)

### Start delimiter (1 byte)
Always set to **7E** in XBee API Mode

### Length (2 bytes)
Number of bytes between Length and Checksum fields

> [!Note]
> The maximum length should be `00 69` or `105` bytes

### Frame type (1 byte)
Specefies XBee API frame type (0x81)

### 16-bit source address (2 bytes)
16-bit network address of the sender device.
Can be set in XTCU (Parameter **MM**).

> [!Note]
> Set to `FF FE` if the sender's 16-bit address is unknown

### Received Signal Strength Indicator (RSSI) (1 byte)
Hexadecimal equivalent of (-dBm) value.

Example:
* For a RX signal strength of -40 dBm, a 28 hexadecimal value (40 decimal) is returned.

### Options (1 byte)
Bitfield indicating the Rx indicator options
* bit 0 - [reserved]
* bit 1 - Address broadcast
* bit 2 - PAN broadcast
* bits 3-7 0 [reserved]

### RF data (0 - 100 bytes)
Packet payload, up to **100** bytes (100 characters)

### Checksum (1 byte)
FF minus 8-bit sum of bytes between length and checksum fields.

## XBee Transmit Status(API Mode - Frame Type 89)
### Start delimiter (1 byte)
Always set to **7E** in XBee API Mode

### Length (2 bytes)
Number of bytes between Length and Checksum fields. Should always be `00 03`

### Frame type (1 byte)
Specefies XBee API frame type (0x89)

### Frame ID (1 byte)
Identifies the UART data frame being reported.
If the Frame ID = 0 in the transmit request, no transmit status is  given

### Delivery Status (1 byte)
ID | Description
:--: | --
00 | Success
01 | An expected MAC acknowledgment never occurred  
02 | CCA failure  
03 | Packet was purged without being transmitted  
04 | Physical error on the interface with the WiFi transceiver  
18 | No Buffers  
21 | Expected network acknowledgment never occurred  
22 | Not joined to network  
23 | Self-addressed  
24 | Address not found  
25 | Route not found  
26 | Broadcast relay was not heard  
2B | Invalid Binding Table Index  
2C | Invalid Endpoint  
31 | A software error occurred  
32 | Resource Error  
40 | CoAP message URI requires a nonzero length URI string terminated with a zero byte  
41 | Unrecognized Digi API Frame type  
42 | Client made a badly formed CoP request  
43 | Server failed to handle CoAP request, perhaps due to a lack of internal resources. The client may try again  
44 | CoAP Invalid Status  
45 | CoAP Message Timeout, Server did not respond within the expected time  
46 | CoAP Message Reset  
74 | Data payload too large  
75 | Indirect message unrequested  
76 | Client socket creation attempt failed  
77 | Connection does not exist  
78 | Invalid UDP port  
79 | Invalid TCP port  
7A | Invalid host  
7B | Invalid data mode  
7C | Invalid interface  
7D | Interface not accepting frames  
80 | Connection refused  
81 | Connection lost  
82 | No server  
83 | Socket closed  
84 | Unknown server  
85 | Unknown error  
86 | Invalid TLS configuration  
BB | Key not authorized  

<!-- An expected MAC acknowledgement never occurred [01]
CCA failure [02]
Packet was purged without being transmitted [03]
Physical error on the interface with the WiFi transceiver [04]
No Buffers [18]
Expected network acknowledgement never occurred [21]
Not joined to network [22]
Self-addressed [23]
Address not found [24]
Route not found [25]
Broadcast relay was not heard [26]
Invalid Binding Table Index [2B]
Invalid Endpoint [2C]
A software error occurred [31]
Resource Error [32]
CoAP message URI requires a nonzero length URI string terminated with a zero byte [40]
Unrecognized Digi API Frame type [41]
Client made a badly formed CoP request [42]
Server failed to handle CoP request, perhaps due to a lack of internal resources. The client may try again [43]
CoAP Invalid Status [44]
CoAP Message Timeout, Server did not respond within the expected time [45]
CoAP Message Reset [46]
Data payload too large [74]
Indirect message unrequested [75]
Client socket creation attempt failed [76]
Connection does not exist [77]
Invalid UDP port [78]
Invalid TCP port [79]
Invalid host [7A]
Invalid data mode [7B]
Invalid interface [7C]
Interface not accepting frames [7D]
Connection refused [80]
Connection lost [81]
No server [82]
Socket closed [83]
Unknown server [84]
Unknown error [85]
Invalid TLS configuration [86]
Key not authorized [BB] -->