# XBee Serial API Usage Guide
This guide provides examples of how to use the XBee API for **GCS and vehicle communication**.

---
## **1️⃣ Initializing the XBee Connection**
This example shows how to **open an XBee connection** before sending or receiving data.

### **Methods Used:**
- `XBee.__init__(port, baudrate, status, logger)`
- `XBee.open()`

### **Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `port` | `str` | Serial port name (e.g., `/dev/cu.usbserial-D30DWZKY`) |
| `baudrate` | `int` | XBee baud rate (default: `115200`) |
| `status` | `bool` | Enable automatic status reception (default: `False`) |
| `logger` | `Logger` | Logger instance for debugging |

### **Returns:**
- `True` if the connection opens successfully.
- `False` if it fails.

> **ℹ️ Note:** `Logger` is not required. It is used for **testing and debugging** in GCS but can be omitted (logger=None).

### **Example:**
```python
from Communication.XBee import XBee
from Logger.Logger import Logger

# Configuration
PORT = "/dev/cu.usbserial-D30DWZKY"
BAUD_RATE = 115200
LOGGER = Logger()

# Initialize XBee
xbee = XBee(port=PORT, baudrate=BAUD_RATE, logger=LOGGER)

# Open XBee connection
if xbee.open():
    print("[INFO] XBee connection opened successfully.")
else:
    print("[ERROR] Failed to open XBee connection.")

## **2️⃣ Closing the XBee Connection**
This example demonstrates how to **properly close the XBee serial connection** when it is no longer needed.

### **Methods Used:**
- `XBee.close()`

### **Returns:**
- `True` if the serial port is successfully closed.
- `False` if the port is already closed or an error occurs.

> **ℹ️ Note:** It is good practice to **always close the XBee connection** when it is no longer in use to free up system resources.

### **Example:**
```python
from Communication.XBee import XBee

# Configuration
PORT = "/dev/cu.usbserial-D30DWZKY"
BAUD_RATE = 115200

# Initialize XBee without Logger
xbee = XBee(port=PORT, baudrate=BAUD_RATE, logger=None)

# Open the XBee connection
if xbee.open():
    print("[INFO] XBee connection opened successfully.")

    # Perform communication tasks here...

    # Close the connection
    if xbee.close():
        print("[INFO] XBee connection closed successfully.")
    else:
        print("[WARNING] XBee was already closed.")
else:
    print("[ERROR] Failed to open XBee connection.")
