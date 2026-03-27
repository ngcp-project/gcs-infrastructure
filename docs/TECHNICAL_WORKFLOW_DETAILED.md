# GCS-Infrastructure: Detailed Technical Workflow

**Date:** March 20, 2026  
**System:** Ground Control Station (GCS) to UGV Manual Control with Sensor Telemetry  
**Architecture:** Multi-process, queue-based, radio-over-XBee with ROS integration

---

## 1. SYSTEM OVERVIEW & ARCHITECTURE

### 1.1 Physical System Components

Your system consists of **three primary nodes**:

1. **GCS (Ground Control Station)** - Operator workstation
2. **Vehicle (UGV)** - Unmanned Ground Vehicle with embedded controller
3. **Firmware Controller** - Dedicated hardware interface on the vehicle communicating with actual actuators/sensors

### 1.2 Communication Stack

```
Layer 1 (Physical):    UART Serial @ 115200 baud
Layer 2 (Radio):       XBee 802.15.4 wireless protocol
Layer 3 (Data):        Binary packet format (C struct packing)
Layer 4 (Application): Command/Telemetry queue abstraction
Layer 5 (Sensor):      ROS publish/subscribe for XSens IMU/GPS data
```

### 1.3 XBee Configuration

- **Baud Rate:** 115200 bps
- **Protocol:** Coordinator (GCS) and Endpoint (Vehicle) nodes
- **MAC Addressing:** 64-bit addresses for point-to-point and broadcast
- **Vehicle MAC Addresses:**
  - MRA (Main Robotics Asset): `0013A200424353F7`
  - MEA: (defined in `lib/gcs-packet/Packet/PacketLibrary/PacketLibrary.py`)
  - ERU: (defined in `lib/gcs-packet/Packet/PacketLibrary/PacketLibrary.py`)

---

## 2. COMMAND FLOW: GCS → Vehicle → Firmware → Hardware

### 2.1 Source: Controller Input (UGV-Manual-Control Subsystem)

**File Location:** [UGV-Manual-Control/](UGV-Manual-Control/)  
**Process:** Xbox gamepad polling at the GCS operator station

**Input Components:**
- [UGV-Manual-Control/ugv_manual_control.py](UGV-Manual-Control/ugv_manual_control.py) - Main controller polling loop
- [UGV-Manual-Control/Controller-Input-Handling/ControllerState.py](UGV-Manual-Control/Controller-Input-Handling/ControllerState.py) - Data class holding all controller state (buttons, triggers, analog sticks)
- [UGV-Manual-Control/Controller-Input-Handling/StateInterpreter.py](UGV-Manual-Control/Controller-Input-Handling/StateInterpreter.py) - Interprets controller state into command tuples

**Controller Input Mapping:**
```
Left Trigger (LT)         → Command ID 6 (VelocityControl) with signed value (-100 to 0 = reverse)
Right Trigger (RT)        → Command ID 6 (VelocityControl) with signed value (0 to 100 = forward)
Left Stick X-axis (LX)    → Command ID 7 (SteeringControl) with signed value (-100 to 100 = left/right)
Right Stick Y-axis (RY)   → Command ID 8 (PayloadControl) with discrete value (1 = raise, -1 = lower)
X Button                  → Command ID 9 (EndEffectorControl) with discrete value (0 = open, 1 = close)
```

**State Interpreter Logic** ([StateInterpreter.py](UGV-Manual-Control/Controller-Input-Handling/StateInterpreter.py)):
- Reads `ControllerState` object with current gamepad state
- Generates list of command tuples `[(command_id, value), ...]`
- Normalizes raw controller values to -100 to 100 scale
- Implements dead-zone logic for analog inputs

**Example Flow:**
```
User presses LT at 50% → StateInterpreter produces → (6, -50)
Meaning: Execute command 6 (VelocityControl) with value -50 (reverse at 50% speed)
```

### 2.2 Command Definition & Encoding (Packet/Command/UGV_Manual_Control_Commands/)

**File Locations:** [Packet/Command/UGV_Manual_Control_Commands/](Packet/Command/UGV_Manual_Control_Commands/)

Each command class inherits from `CommandInterface` and implements:
- `encode_packet(data)` - Serializes command to binary
- `decode_packet(binary)` - Deserializes binary to Python types

**Command Specifications:**

| Class | Cmd ID | Payload Format | Data Range | Purpose |
|-------|--------|----------------|-----------|---------|
| [VelocityControl.py](Packet/Command/UGV_Manual_Control_Commands/VelocityControl.py) | 6 | `BBb` (Payload ID, Cmd ID, Velocity) | -100 to +100 | Forward/reverse motion |
| [SteeringControl.py](Packet/Command/UGV_Manual_Control_Commands/SteeringControl.py) | 7 | `BBb` | -100 to +100 | Left/right wheel steering |
| [PayloadControl.py](Packet/Command/UGV_Manual_Control_Commands/PayloadControl.py) | 8 | `BBB` | 0-2 (discrete) | Raise/lower payload arm |
| [EndEffectorControl.py](Packet/Command/UGV_Manual_Control_Commands/EndEffectorControl.py) | 9 | `BBB` | 0-1 (discrete) | Open/close end effector (gripper) |
| [ToggleManualControl.py](Packet/Command/UGV_Manual_Control_Commands/ToggleManualControl.py) | 5 | TBD | TBD | Enable/disable manual control mode |

**Struct Packing Format Explanation:**
- `B` = unsigned char (1 byte)
- `b` = signed char (1 byte)
- Example: `VelocityControl` FORMAT_STRING `"BBb"` = 3 bytes total
  - Byte 0: PayloadID = 1 (always)
  - Byte 1: CommandID = 6 (identifies command type)
  - Byte 2: Velocity value (signed, -128 to +127, normalized to -100 to +100)

**Encoding Example:**
```python
# User input: Full right trigger (RT = 100)
velocity_value = 100
encoded = VelocityControl.encode_packet(100)
# Result: b'\x01\x06\x64'  (hex: 01 06 64)
# Breakdown: 01=PayloadID, 06=CommandID, 64=100 in decimal
```

### 2.3 Queue Management (Application/Infrastructure/)

**File Locations:** 
- [Application/Infrastructure/PacketQueue.py](Application/Infrastructure/PacketQueue.py) - Queue definitions
- [Application/Infrastructure/InfrastructureInterface.py](Application/Infrastructure/InfrastructureInterface.py) - Queue API

**Queue System:**
```python
CommandQueue = Queue(maxsize=0)       # Unbounded FIFO for outgoing commands
TelemetryQueue = Queue(maxsize=0)     # Unbounded FIFO for incoming telemetry
```

**Queue Operations:**
```python
# Sending a command (GCS side)
SendCommand(VelocityControl.encode_packet(100), Vehicle.MRA)
# → Internally calls: CommandQueue.put(encoded_bytes)

# Receiving a command (Vehicle side)
command = ReceiveCommand()  # Blocks until item available
# → Internally calls: CommandQueue.get() and task_done()
```

**Thread Safety:** Python's `queue.Queue` is thread-safe; blocking operations ensure proper synchronization between input threads and transmission threads.

### 2.4 Radio Transmission (Application/Infrastructure/GCSXBee.py)

**File Location:** [Application/Infrastructure/GCSXBee.py](Application/Infrastructure/GCSXBee.py)

**Function:** `StartGCSXBee(PORT: str)`

**Architecture:**
- Launches two persistent daemon threads:
  1. **CommandThread** - Monitors `CommandQueue`, encodes, transmits via XBee
  2. **TelemetryThread** - Monitors XBee for incoming telemetry, decodes, queues

**Command Transmission Flow:**

```
1. GCS sends command via InfrastructureInterface.SendCommand()
   → Command object pushed to CommandQueue

2. GCSXBee.RunCommandThread() (running in background):
   a. Blocks on CommandQueue.get() waiting for item
   b. Receives encoded command bytes
   c. Identifies target vehicle from Vehicle enum
   d. Looks up MAC address via PacketLibrary.GetMACAddressFromVehicle()
   e. Calls xbee.transmit_data(encoded_bytes, target_mac)
   f. XBee module sends binary packet over radio
   g. Marks queue item as task_done()
   h. Loops back to step 2b

3. XBee Radio Transmission:
   a. Packet formatted as XBee 802.15.4 frame
   b. Includes destination MAC address, payload length, data, checksum
   c. Transmitted wirelessly to receiving XBee module
   d. Physical transmission at 115200 bps serial rate
```

**Vehicle Broadcast:** Commands with `Vehicle.ALL` are transmitted to all three vehicles:
```python
if CommandInstance.Vehicle == Vehicle.ALL:
    for mac in [MRA_MAC, MEA_MAC, ERU_MAC]:
        xbee.transmit_data(EncodedCommand, mac)
```

### 2.5 Vehicle Reception & Decoding (Application/Infrastructure/VehicleXBee.py)

**File Location:** [Application/Infrastructure/VehicleXBee.py](Application/Infrastructure/VehicleXBee.py)

**Function:** `StartVehicleXBee(PORT: str)`

**Architecture:**
- Launches two persistent daemon threads (symmetric to GCS side):
  1. **CommandThread** - Monitors XBee for incoming commands, decodes, queues
  2. **TelemetryThread** - Monitors `TelemetryQueue`, encodes, transmits via XBee

**Command Reception Flow:**

```
1. XBee Wireless Reception:
   a. Physical XBee module receives radio packet
   b. Deframes XBee 802.15.4 structure
   c. Extracts source MAC, payload data, RSSI
   d. Passes to xbee.retrieve_data() as frame object

2. VehicleXBee.RunCommandThread() (running in background):
   a. Calls xbee.retrieve_data() - blocks until packet received
   b. Extracts binary payload from frame (e.g., b'\x01\x06\x64')
   c. Inspects first byte (command type identifier)
   d. Uses match statement to dispatch to correct decoders:
      - Byte value 1 → Heartbeat.DecodePacket()
      - Byte value 2 → EmergencyStop.DecodePacket()
      - ... etc ...
      - Byte value 6 → VelocityControl.DecodePacket()  ← Manual control velocity
   e. Decoder unpacks binary struct into Python types
   f. Creates CommandInstance object
   g. Pushes to CommandQueue
   h. Loops back to step 2a

3. Command Queuing:
   a. Decoded command object waits in CommandQueue
   b. Firmware thread (YOUR RESPONSIBILITY) calls ReceiveCommand()
   c. Blocks until item available, then receives CommandInstance
   d. Applies command to actual hardware (motors, servos, etc.)
```

**Decode Example:**
```python
received_bytes = b'\x01\x06\x64'  # Binary payload from XBee

struct.unpack("BBb", received_bytes)
# Returns: (1, 6, 100)  # PayloadID=1, CommandID=6, Velocity=100

# CommandID 6 → Route to VelocityControl decoder
velocity = VelocityControl.decode_packet(received_bytes)
# Returns: 100 (the signed velocity value)
```

### 2.6 Firmware Integration Point

**⚠️ YOUR IMPLEMENTATION RESPONSIBILITY:**

The command reaches your firmware as a decoded Python object in `CommandQueue`. Your firmware thread must:

1. Call `ReceiveCommand()` from [InfrastructureInterface.py](Application/Infrastructure/InfrastructureInterface.py)
2. Wait for command (blocking call)
3. Determine command type (check CommandID)
4. Extract data (speed, angle, etc.)
5. Convert to firmware protocol (CAN, SPI, direct GPIO, etc.)
6. Send to actual hardware controllers

**Example Pseudo-code for Your Firmware Interface:**
```python
from Application.Infrastructure.InfrastructureInterface import ReceiveCommand

def firmware_control_loop():
    while True:
        command = ReceiveCommand()  # Blocks until GCS sends
        
        if command.CommandID == 6:  # VelocityControl
            speed = command.decode_packet(...)
            can_bus.send(CANMessage(MOTOR_CMD, speed))
        
        elif command.CommandID == 7:  # SteeringControl
            angle = command.decode_packet(...)
            pwm.set_duty_cycle(SERVO_PIN, angle)
        
        # ... more command handlers ...
```

---

## 3. TELEMETRY FLOW: XSens → Vehicle → GCS

### 3.1 Source: XSens IMU/GPS Sensor via ROS

**File Location:** [XSens/src/xsens_ros_mti_driver/](XSens/src/xsens_ros_mti_driver/)

**Hardware:** Xsens MT Motion Tracking sensor (IMU with GPS/GNSS)

**ROS Architecture:**
- **Driver Node:** `xsens_mti_node` - Communicates with hardware via USB/serial
- **Published Topics** (at configurable rate, default 1 Hz):
  - `/filter/positionlla` - Latitude, longitude, altitude (LLA) coordinates
  - `/filter/euler` - Pitch, roll, yaw angles (Euler representation)
  - `/filter/velocity` - Linear velocity in 3D space
  - `/status` - Device status and health

**Broadcasting Rate:** Configurable via ROS parameter `send_rate_hz` (launch parameter)

**Data Format:** Standard ROS message types (geometry_msgs, sensor_msgs)

### 3.2 Bridge: ROS-to-XBee Converter

**File Location:** [XSens/src/xsens_ros_mti_driver/xsens_to_gcs_bridge.py](XSens/src/xsens_ros_mti_driver/xsens_to_gcs_bridge.py)

**Purpose:** Subscribe to ROS sensor topics and serialize into XBee telemetry packets

**Architecture:**
```
ROS Subscriber                XBee Transmitter
┌─────────────────────────┐
│ /filter/positionlla     │
│ /filter/euler           │ → Telemetry Serializer → XBee.transmit_data()
│ /filter/velocity        │   (applies gcs-packet lib  → Vehicle MAC
│ /status                 │    Telemetry.Encode())    (broadcasts to GCS)
└─────────────────────────┘
```

**Bridge Algorithm:**

```
1. Initialize ROS node and subscribe to sensor topics
2. Initialize XBee serial connection to specified port

3. Run Loop at send_rate_hz:
   a. Fetch latest messages from topic buffers (callbacks populate these)
   b. Extract sensor values:
      - Position: lat, lon, alt from positionlla
      - Orientation: pitch, roll, yaw from euler
      - Speed: norm(velocity vector) from velocity
   c. Create Telemetry object:
      telemetry = Telemetry(
          Speed = calculated_speed,
          Pitch = pitch,
          Yaw = yaw,
          Roll = roll,
          Altitude = alt,
          BatteryLife = parameter_battery_life_default,
          CurrentPosition = (lat, lon),
          VehicleStatus = 0 (operational),
          MessageFlag = parameter_message_flag_default,
          ... other fields ...
      )
   d. Call Telemetry.Encode() → produces 72-byte binary packet
   e. Transmit packet via XBee:
      xbee.transmit_data(encoded_bytes, GCS_MAC_ADDRESS)
   f. Wait for next send cycle or update if new data arrives
```

**Telemetry Packet Structure** (72 bytes total):

| Offset | Field | Type | Bytes | Example |
|--------|-------|------|-------|---------|
| 0 | CommandID | unsigned int | 1 | 0 |
| 1 | PacketID | unsigned char | 1 | 0 |
| 2-5 | Speed | float | 4 | 2.5 (m/s) |
| 6-9 | Pitch | float | 4 | -15.3° |
| 10-13 | Yaw | float | 4 | 45.2° |
| 14-17 | Roll | float | 4 | 5.1° |
| 18-21 | Altitude | float | 4 | 120.5 (meters) |
| 22-25 | BatteryLife | float | 4 | 85.0 (%) |
| 26-33 | LastUpdated | unsigned long | 8 | Unix timestamp |
| 34-37 | PositionX (Lat) | double | 8 | 37.7749 |
| 38-45 | PositionY (Lon) | double | 8 | -122.4194 |
| 46 | VehicleStatus | unsigned char | 1 | 0 (OK) |
| 47 | MessageFlag | unsigned char | 1 | 0 (none) |
| 48-55 | MessageLat | double | 8 | 37.7749 |
| 56-63 | MessageLon | double | 8 | -122.4194 |
| 64 | PatientStatus | unsigned char | 1 | 0 |

**Struct Format String:**
```python
FORMAT_STRING = "=BI6fQ2d2B2dB"
# =     : standard size/packing
# B     : 1 CommandID
# I     : 1 PacketID (4 bytes)
# 6f    : 6 floats (24 bytes) - Speed, Pitch, Yaw, Roll, Altitude, BatteryLife
# Q     : 1 unsigned long (8 bytes) - LastUpdated
# 2d    : 2 doubles (16 bytes) - Position X/Y
# 2B    : 2 unsigned chars (2 bytes) - VehicleStatus, MessageFlag
# 2d    : 2 doubles (16 bytes) - MessageLat/Lon
# B     : 1 PatientStatus
```

### 3.3 Vehicle XBee Telemetry Transmission

**File Location:** [Application/Infrastructure/VehicleXBee.py](Application/Infrastructure/VehicleXBee.py)

**Function:** `StartVehicleXBee(PORT: str)` - TelemetryThread

**Flow:**

```
1. TelemetryQueue contains Telemetry objects (from XSens bridge)

2. VehicleXBee.RunTelemetryThread() (running in background):
   a. Blocks on TelemetryQueue.get()
   b. Receives Telemetry instance
   c. Validates it's a Telemetry object type
   d. Calls TelemetryInstance.Encode()
      → Returns 72-byte binary packet
   e. Transmits to GCS:
      xbee.transmit_data(encoded_bytes, 
                         PacketLibrary.GetGCSMACAddress())
   f. Marks queue item as task_done()
   g. Loops back to step 2a
```

### 3.4 GCS Reception & Display

**File Location:** [Application/Infrastructure/GCSXBee.py](Application/Infrastructure/GCSXBee.py)

**Function:** `StartGCSXBee(PORT: str)` - TelemetryThread

**Flow:**

```
1. GCSXBee.RunTelemetryThread() (running in background):
   a. Calls xbee.retrieve_data() - blocks until packet received
   b. Extracts payload bytes
   c. Calls Telemetry.Decode(payload)
      → Returns Telemetry object with all fields populated
   d. Attaches metadata:
      - Vehicle identification (MAC → Vehicle enum mapping)
      - MACAddress attribute
   e. Pushes to TelemetryQueue
   f. Loops back to step 1a

2. GCS Application receives telemetry:
   a. Calls ReceiveTelemetry() from InfrastructureInterface
   b. Telemetry object returned
   c. Application/UI displays:
      - Vehicle speed and position
      - Orientation (pitch/roll/yaw)
      - Battery level
      - Sensor status
```

---

## 4. SYNCHRONIZATION & TIMING

### 4.1 Command Latency

```
GCS Input → Encode (1ms) → Queue (0ms) → XBee transmit thread (5-10ms) 
→ Radio flight time (varies by distance) → Vehicle XBee (5-10ms) 
→ Decode (1ms) → Firmware thread reception (blocking until next poll)
≈ 15-50ms typical end-to-end latency (excluding radio propagation)
```

### 4.2 Telemetry Update Rate

- **XSens sensor polling:** Device-dependent (usually 100 Hz internal)
- **ROS publish rate:** Configurable; default 1 Hz
- **Bridge send rate:** Configurable `send_rate_hz` parameter (ROS launch)
- **GCS display refresh:** Depends on application polling `ReceiveTelemetry()`

### 4.3 Thread Safety Mechanisms

**Queue-based coordination:**
- Python's `queue.Queue` is intrinsically thread-safe
- No manual locks needed in current architecture
- Blocking get/put operations handle producer-consumer synchronization

**Event-based shutdown:** (Currently not fully implemented)
- `CommandStopEvent` and `TelemetryStopEvent` planning for graceful shutdown
- Threads check `.is_set()` periodically (not on every loop)

---

## 5. ERROR HANDLING & ROBUSTNESS

### 5.1 Current Exception Handling

**GCS Command Thread:**
```python
except queue.Empty as e:
    print(f"Error: {e}")  # Timeout on queue.get()
except Exception as e:
    print(f"Error: {e}")  # Catches all other exceptions
```

**Vehicle Command Thread:**
```python
except Exception as e:
    print(f"Error: {e}")  # Catches serial errors, decode errors, etc.
```

**Limitations:**
- No retry mechanism for failed transmissions
- No acknowledgment protocol for critical commands
- No timeout handling for lost radio connectivity
- Errors logged but may not halt gracefully

### 5.2 Data Validation

**Telemetry Decode Validation:**
```python
if len(BinaryData) != ExpectedSize:  # 72 bytes
    print(f"Invalid telemetry packet size...")
    return None
```

**Command Bounds Checking:**
- VelocityControl: -100 to +100 (normalized, not enforced in decode)
- SteeringControl: -100 to +100
- EndEffector/Payload: 0-1 or 0-2 (discrete)

### 5.3 Recommended Improvements

1. **Heartbeat mechanism:** Periodic keep-alive packets from vehicle
2. **Command ACK protocol:** Vehicle confirms receipt of critical commands
3. **Timeout handlers:** Close connections if no rx/tx for N seconds
4. **CRC validation:** Add checksum to custom packets beyond XBee checksum
5. **Graceful degradation:** Continue operating on single vehicle failure

---

## 6. DEPLOYMENT & RUNTIME

### 6.1 GCS Machine Setup

```bash
# Terminal A: GCS XBee receiver
cd /Users/aro/Documents/gcs-infrastructure
source .venv/bin/activate
export PYTHONPATH="$PWD/Application:$PYTHONPATH"
python3 <<'PY'
from Infrastructure.InfrastructureInterface import LaunchGCSXBee, ReceiveTelemetry
PORT = "/dev/tty.usbserial-YOUR_GCS_PORT"  # Replace with actual port
LaunchGCSXBee(PORT)
print("GCS receiver started")
while True:
    telemetry = ReceiveTelemetry()
    print(telemetry)
PY
```

### 6.2 Vehicle Machine Setup

```bash
# Terminal C: XSens + Bridge
cd /Users/aro/Documents/gcs-infrastructure/XSens
source /opt/ros/noetic/setup.bash
source devel/setup.bash
roslaunch xsens_mti_driver xsens_mti_with_gcs_bridge.launch \
  xbee_port:=/dev/ttyUSB0 \
  send_rate_hz:=1.0 \
  battery_life_default:=85.0 \
  patient_status_default:=0 \
  message_flag_default:=0 \
  message_lat_default:=0.0 \
  message_lon_default:=0.0
```

### 6.3 Port Configuration

**GCS XBee Port:** Typically `/dev/cu.usbserial-XXXXXXXXXX` (macOS) or `COM3` (Windows)  
**Vehicle XBee Port:** Typically `/dev/ttyUSB0` (Linux) or `COM4` (Windows)  

Determine ports:
```bash
# macOS
ls -l /dev/cu.usb*

# Linux
ls -l /dev/ttyUSB*

# Windows
# Device Manager → COM ports
```

### 6.4 MAC Address Configuration

**Critical:** Update GCS MAC in firmware before deployment

File: [lib/gcs-packet/Packet/PacketLibrary/PacketLibrary.py](lib/gcs-packet/Packet/PacketLibrary/PacketLibrary.py)

```python
GCS_MAC_ADDRESS = "0013A20042435A3D"  # Replace with actual GCS XBee MAC
```

Determine MAC address:
```python
from xbee import XBee
xbee = XBee(port="/dev/cu.usbserial-PORT", baudrate=115200)
xbee.open()
mac = xbee.get_own_address()  # 64-bit MAC as hex string
print(mac)
```

---

## 7. PACKET LIBRARY & VEHICLE MAPPING

**File:** [lib/gcs-packet/Packet/PacketLibrary/PacketLibrary.py](lib/gcs-packet/Packet/PacketLibrary/PacketLibrary.py)

**Central registry mapping vehicles to MAC addresses:**

```python
class PacketLibrary:
    GCS_MAC_ADDRESS = "0013A2004243XXXX"  # Your GCS MAC
    
    VEHICLE_MAC_MAP = {
        Vehicle.MRA: "0013A200424353F7",
        Vehicle.MEA: "0013A200XXXXXXXX",
        Vehicle.ERU: "0013A200XXXXXXXX",
    }
    
    @staticmethod
    def GetMACAddressFromVehicle(vehicle: Vehicle) -> str:
        return VEHICLE_MAC_MAP.get(vehicle)
    
    @staticmethod
    def GetVehicleFromMACAddress(mac: str) -> Vehicle:
        # Reverse lookup
        for vehicle, vehicle_mac in VEHICLE_MAC_MAP.items():
            if vehicle_mac == mac:
                return vehicle
        return Vehicle.UNKNOWN
```

---

## APPENDIX: File Structure Quick Reference

```
/Users/aro/Documents/gcs-infrastructure/
├── Application/
│   ├── Infrastructure/
│   │   ├── InfrastructureInterface.py    ← Queue API entry point
│   │   ├── GCSXBee.py                    ← GCS radio management (TX/RX threads)
│   │   ├── VehicleXBee.py                ← Vehicle radio management (TX/RX threads)
│   │   ├── PacketQueue.py                ← Queue definitions
│
├── Packet/
│   └── Command/
│       └── UGV_Manual_Control_Commands/
│           ├── VelocityControl.py        ← Cmd ID 6
│           ├── SteeringControl.py        ← Cmd ID 7
│           ├── PayloadControl.py         ← Cmd ID 8
│           ├── EndEffectorControl.py     ← Cmd ID 9
│           └── ToggleManualControl.py    ← Cmd ID 5
│
├── UGV-Manual-Control/
│   ├── ugv_manual_control.py             ← Controller polling
│   └── Controller-Input-Handling/
│       ├── ControllerState.py            ← Button/stick data class
│       └── StateInterpreter.py           ← Convert state → commands
│
├── XSens/
│   └── src/
│       ├── xsens_ros_mti_driver/
│       │   └── xsens_to_gcs_bridge.py    ← ROS subscriber → XBee transmitter
│       └── ntrip/
│
├── lib/
│   ├── gcs-packet/
│   │   └── Packet/
│   │       ├── Telemetry/
│   │       │   └── Telemetry.py          ← 72-byte packet encode/decode
│   │       └── PacketLibrary/
│   │           └── PacketLibrary.py      ← MAC address registry
│   │
│   └── xbee-python/
│       └── src/xbee/
│           └── XBee.py                   ← XBee radio interface (UART driver)
│
└── docs/
    ├── full-lifecycle.md                 ← Deployment commands
    └── xsens-to-gcs-code-explained.md   ← Bridge implementation details
```

---

## SUMMARY: Who Talks to Whom

```
┌──────────────────┐
│   GCS Operator   │ (Presses Xbox controller buttons)
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────┐
│  UGV-Manual-Control Subsystem│ (Polls controller, interprets input)
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  Packet/Command Encoders     │ (Serializes to binary payload, e.g., b'\x01\x06\x64')
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  GCS InfrastructureInterface  │ (Queues encoded command)
│  CommandQueue.put(...)       │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  GCSXBee CommandThread        │ (Blocks on CommandQueue, transmits via XBee radio)
└────────┬─────────────────────┘
         │  (XBee 802.15.4 wireless  )
         │    @ 115200 baud UART    
         ▼
     [OVER THE AIR]
         │
         ▼
┌──────────────────────────────┐
│  Vehicle XBee (Receiver)      │ (Deframed data from radio)
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  VehicleXBee CommandThread    │ (Retrieve data, dispatch to decoders)
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  Packet/Command Decoders      │ (Deserialize binary to Python types)
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  Vehicle InfrastructureQueue  │ (CommandQueue.put(decoded_command))
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  YOUR FIRMWARE TEAM          │ (ReceiveCommand() from queue)
│  • Convert to CAN/SPI/GPIO   │
│  • Control motors, servos    │
│  • Interface actual hardware │
└──────────────────────────────┘

═══════════════════════════════════════

REVERSE PATH: Telemetry (XSens → GCS)

┌──────────────────────────────┐
│  XSens IMU/GPS Sensor        │ (Continuously measures orientation, position)
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  ROS xsens_mti_node Driver   │ (Publishes to /filter/* topics @ 100 Hz)
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  xsens_to_gcs_bridge.py      │ (Subscribes to ROS topics @ send_rate_hz)
│  • Extracts pitch, roll, yaw │
│  • Extracts lat, lon, alt    │
│  • Extracts speed            │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  Telemetry.Encode()          │ (Packs 72-byte binary structure)
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  VehicleXBee TelemetryThread │ (TelemetryQueue.get(), transmit via XBee)
└────────┬─────────────────────┘
         │  (XBee 802.15.4 wireless)
         │    @ 115200 baud UART    
         ▼
     [OVER THE AIR]
         │
         ▼
┌──────────────────────────────┐
│  GCS XBee (Receiver)         │ (Deframed data from radio)
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  GCSXBee TelemetryThread     │ (Retrieve data, call Telemetry.Decode())
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  Telemetry.Decode()          │ (Unpack 72-byte binary structure)
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  GCS InfrastructureQueue     │ (TelemetryQueue.put(decoded_telemetry))
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  GCS Application/Dashboard   │ (ReceiveTelemetry() from queue)
│  • Display vehicle position  │
│  • Show vehicle orientation  │
│  • Display battery status    │
│  • Monitor sensor health     │
└──────────────────────────────┘
```

---

**Document Version:** 1.0  
**Last Updated:** March 20, 2026  
**Author:** System Architecture Analysis  
