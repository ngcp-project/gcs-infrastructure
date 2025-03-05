# XBee Serial API
## Constructor


> ```py
> __init__(port=None, baudrate=115200, status=False, logger=None)
>```

Configure the serial port

> [!NOTE]
> Serial ports are not opened on object creation.


**Parameters:**
* **port** (str or None) - Port of serial device.
* **baudrate** (int) - Baudrate of serial device.
* **status** (bool) - Automatically receive status packets after a transmission.
* **logger** (Logger) - Logger object from Logger.Logger used to record data such as sent and received data.

See [Serial Port][serial_port] for details on finding the correct serial port name.

*baudrate* should be the same for both device (XBee RF module) and serial port. XBees will be configured to 115200 by default.

See [Frame Details][transmit_status] for details regarding the XBee status packet (Frame type 0x89).

A Logger instance will be created if it is not provided.

**Example:**

```py
from Communication.XBee.XBee import XBee

PORT = "/dev/cu.usbserial-D30DWZKT"
BAUD_RATE = 115200
xbee = XBee(PORT, BAUD_RATE) # status and logger will be set to False and None respectively
```

## Methods

> ```py
> open()
>```
Open a connection over the serial port.

**Returns:** 
* **True** if success, **False** if failure.

**Return type:** 
* bool

**Throws:**
* **SerialException** - if there is an error opening the serial port

> ```py
> open()
>```
Open a connection over the serial port.

| <!-- --> | <!-- --> |
| - | - |
| **Returns** | **True** if success, **False** if failure. |
| **Return type** | bool | 
| **Throws:** | **SerialException** - if there is an error opening the serial port |

| | |
| - | - |
| **Returns** | **True** if success, **False** if failure. |
| **Return type** | bool | 
| **Throws:** | **SerialException** - if there is an error opening the serial port |

> ```py
> close()
> ```

Close a connection over the serial port.

**Returns:**
* **True** if success, **False** if failure.

> `transmit_data(string data, string address)`

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

[serial_port]: ./serial_port.md
[frame_details]: ./frame_details.md
[transmit_status]: ./frame_details.md#xbee-transmit-statusapi-mode---frame-type-89