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

