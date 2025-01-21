# XBee Serial Library

## Quickstart

* TO DO

### Finding the serial port (device name)
#### Mac
1. Plug in XBee RF module
2. Run `ls -l /dev/cu.usb`
3. The device name should look similar to this:

`/dev/cu.usbserial-D30DWZKT`

#### Linux

...

#### Windows

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
Specefies XBee API frame type 

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
