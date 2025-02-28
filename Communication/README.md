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

1. Plug in XBee RF module
2. Run `ls -l /dev/ttyUSB*` ?

### Windows

1. Plug in XBee RF module
2. 

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

## AT Command (API Mode - Frame Type 08)

### Start delimiter (1 byte)

### Length (2 bytes)

### Frame Type (1 byte)

### Frame ID (1 byte)

### AT command (2 bytes)
<!-- Networking
Parameter ID | Name | Default | Description | Options
:--: | :--: | :--: | -- | --
CH | Channel | C | **Range: [0x0B - 0x1A]** The operating channel number (Uses IEEE 802.15.4 channel numbers).  Only modules with a matching CH can communicate with each other.
ID | Network PAN ID | 3332 | **Range: [0x0 - OxFFFF]** The network PAN (Personal Area Network) ID. Only modules with a matching ID can communicate with each other. Set ID = OxFFFF to send message to all PANs.
MM | MAC Mode | 0 | Configure the MAC Mode of the device. This enables/disables a Digi-proprietary header in the 802.15.4 RF packet and whether or not MAC ACKs should be used. Enabling the Digi header (MM = 0 or 3) allows duplicate packet detection and network discovery via ND and DN commands. Options 1 and 2 are strict 802.15.4 modes which are compatible with some third-party 802.15.4 devices. | <ul><li>802.15.4 + Digi header w/ACKS [0]</li><li>Strict 802.15.4 no ACKs [1]</li><li>Strict 802.15.4 with ACKs [2]</li><li>802.15.4 + Digi header no ACKS [3]</li></ul> 
C8 | Compatibility Options
NI | Node Identifier -->

Networking
* CH Channel
* ID Network PAN ID
* MM MAC Mode
* C8 Compatibility Options
    
    Discovery Options
    * NI Node Identifier
    * DD Device Type Identifier
    * NT Node Discover Time
    * NO Node Discovery Options
    
    Coordinator/End Device Configuration
    * CE Device Role
    * A1 End Device Association
    * A2 Coordinator Association
    * SC Scan Channels
    * AI Association Indication

Addressing
* SH Serial Number High
* SL Serial Number Low
* MY 16-bit Source Address
* DH Destination Address High
* DL Destination Address Low
* RR XBee Retries
* TO Transmit Options
* NP Maximum Packet Payload Length

Security
* EE AES Encryption Enable
* KY AES Encryption Key
* DM Disable Device Functionality
* US OTA Update Server
* SA Secure Access Options
* [NO PARAMETER ID] Secure Session Authentication

Interfacing
* PL TX Power Level
* PP Output power in dBm
* CA CCA Threshold
* RN Random Delay Slots

    MAC Diagnostics
    * DB Last Packet RSSI
    * EA ACK Failures
    * EC CCA Failures

Sleep Settings
* SM Sleep Mode
* SP Sleep Time
* ST Wake Time
* DP Disassociated Cyclic Sleep Period
* SN Number of Cyclic Sleep Periods
* SO Sleep Options

Bluetooth Options
* BT Bluetooth Enable
* BL Bluetooth MAC Address
* BI Bluetooth Identifier
* BP BLE Advertisement Power Level
* [NO PARAMETER ID] Bluetooth Authentication

API Configuration
* AP API Enable
* AO API Output Mode
* AZ Extend API Options

UART Interface
* BD UART Baud Rate
* NB UART Parity
* SB UART Stop Bits
* FT Flow Control Threshold
* RO Transparent Packetization Timeout

    AT Command Options
    * CC Command Sequence Character
    * CT AT Command Mode Timeout
    * GT Guard Times

    UART Pin Configuration
    * D6 DIO6/RTS Configuration
    * D7 DIO7/CTS Configuration
    * P3 DIO13/UART_DOUT Configuration
    * P4 DIO14/UART_DIN Configuration

I/O Settings
* DO DIOO/ADO/Commissioning Button Configuration
* D1 DIO1/AD1/SPI_nATTN Configuration
* D2 DI02/AD2/SPI_CLK Configuration
* D3 DIO3/AD3/SPI_nSSEL Configuration
* D4 DIO4/SPI_MOSI Configuration
* D5 DIO5 Association LED Configuration
* D8 DI08/DTR/Sleep_Rq Configuration
* D9 DIO9 Sleep Indicator Configuration
* P2 DI012/SPI_MISO Configuration
* PR Pull-up/down Resistor Enable
* PD Pull-up/down Direction
* LT Associate LED Blink Time

    I/O Sampling
    * IR IO Sampling Rate
    * IC Digital I/O Change Detection
    * AV Analog Voltage Reference
    * IT Samples before TX
    * IF Sleep Sample Rate

    I/O Line Passing
    * IA I/O Input Address
    * IU Enable Serial Output For I/O Line Passing
    * TO DO Output Timeout
    * T1 D1 Output Timeout
    * T2 D2 Output Timeout
    * T3 D3 Output Timeout
    * T4 D4 Output Timeout
    * T5 D5 Output Timeout
    * T6 D6 Output Timeout
    * T7 D7 Outout Timeout
    * T8 D8 Output Timeout
    * T9 D9 Output Timeout
    * Q0 PO Output Timeout
    * Q1 P1 Output Timeout
    * Q2 P2 Output Timeout

Location
* LX Location X - Latitude
* LY Location Y - Longitude
* LZ Location Z - Elevation

Diagnostics - Firmware/Hardware Information
* VR Firmware Version
* VH Bootloader Version
* HV Hardware Version
* %C Hardware/Firmware Compatibility
* R? Power Variant
* %V Supply Voltage
* TP Temperature
* CK Configuration Checksum
### Parameter value (0 - 256 bytes)

### Checksum

## AT Command Response (API MODE - Frame Type 88)

### Start delimiter (1 byte)

### Length (2 bytes)

### Frame Type (1 byte)

### Frame ID (1 byte)

### AT command (2 bytes)

### Command Status (1 byte)

Status Code | Description
:--: | --
00 | OK
01 | ERROR
02 | Invalid Command
03 | Invalid Parameter
04 | Tx Failure

### Command Data (0 - 256 bytes)
Register data in binary format. If the register was set in the AT Command, then this field is not returned.

### Checksum
FF minus 8-bit sum of bytes between length and checksum fields.