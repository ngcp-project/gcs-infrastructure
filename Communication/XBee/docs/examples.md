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
```

<br>

## **2️⃣ Closing the XBee Connection**
This example demonstrates how to **properly close the XBee serial connection** when it is no longer needed.

### **Methods Used:**
- XBee.close()

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
```

<br>

## **3️⃣ Sending Data to a Specified XBee Address**
This example demonstrates how to **send data from GCS to a vehicle (or any XBee module)** using the `transmit_data()` method.

### **Methods Used:**
- `XBee.transmit_data(data, address, retrieveStatus)`

### **Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `str` | The message or command to be sent. |
| `address` | `str` | The 64-bit address of the destination XBee module. Use `"0000000000000000"` for **broadcast**. |
| `retrieveStatus` | `bool` | If `True`, retrieves a transmit status response. |

### **Returns:**
- `True` if the transmission is **successful**.
- `False` if the **serial port is closed** or an error occurs.

> **ℹ️ Note:** This method **does not confirm** whether the message was delivered successfully to the target. You should check the **Transmit Status Frame (`0x89`)** to confirm delivery. This method is still work-in-progress. Once the functionality of receiving a **Transmit Status Frame (`0x89`)**  is implemented, a new example will be added.

### **Example:**
```python
from Communication.XBee import XBee

# Configuration
PORT = "/dev/cu.usbserial-D30DWZKY"
BAUD_RATE = 115200
DEST_ADDRESS = "0013A20040B5XXXX"  # Replace with actual 64-bit address

# Initialize XBee without Logger
xbee = XBee(port=PORT, baudrate=BAUD_RATE, logger=None)

# Open XBee connection
if xbee.open():
    print("[INFO] XBee connection opened successfully.")

    # Message to send
    message = "Hello Vehicle, this is GCS!"

    # Send data to the specified XBee address
    if xbee.transmit_data(data=message, address=DEST_ADDRESS, retrieveStatus=False):
        print(f"[INFO] Data sent to {DEST_ADDRESS} successfully.")
    else:
        print(f"[ERROR] Failed to send data to {DEST_ADDRESS}.")

    # Close XBee connection after sending data
    xbee.close()
else:
    print("[ERROR] Failed to open XBee connection.")
```

