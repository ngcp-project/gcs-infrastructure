# GCS Infrastructure: Workflow Overview (PDR Version)

**System Name:** UGV Ground Control & Telemetry System  
**Prepared For:** Preliminary Design Review (PDR)

---

## EXECUTIVE SUMMARY

This system enables bidirectional wireless communication between a Ground Control Station (GCS) operator and an Unmanned Ground Vehicle (UGV). The operator uses an Xbox controller to command vehicle motion, while the vehicle's XSens IMU/GPS sensor transmits real-time orientation and position data back to the GCS. All communication occurs via XBee 802.15.4 radio modules at 115200 baud.

---

## SYSTEM ARCHITECTURE

```
┌─────────────────┐                    ┌──────────────────────┐
│   GCS Operator  │                    │  UGV with Firmware   │
│                 │                    │  & XSens Sensor      │
│  Xbox Controller│                    │                      │
└────────┬────────┘                    └──────────────┬───────┘
         │                                           │
         │ COMMAND FLOW (GCS → Vehicle)              │
         ▼                                           ▼
    ┌────────────┐      XBee Radio       ┌─────────────────┐
    │ GCS XBee   │◄─────────────────────►│ Vehicle XBee    │
    │ Transmitter│      (115200 baud)    │ Receiver        │
    └────────────┘                        └─────────────────┘
         ▲                                           │
         │                                           │ Firmware Interface
         │ TELEMETRY (Vehicle → GCS)                 │ (YOUR RESPONSIBILITY)
         │                                           ▼
         │                       ┌──────────────────────────┐
         │                       │  Hardware Controllers    │
         │                       │  (Motors, Servos, etc.)  │
         │                       └──────────────────────────┘
         │
    ┌─────────────────────────────────────┐
    │  XSens Sensor Data                  │
    │  (Pitch, Roll, Yaw, Position)       │
    │  via ROS topics                     │
    └─────────────────────────────────────┘
```

---

## SYSTEM COMPONENTS

### **1. Command Input Pipeline**

| Stage | Component | Input | Output |
|-------|-----------|-------|--------|
| A | Xbox Controller | Button/stick input | Raw gamepad state |
| B | [Controller Interpreter](UGV-Manual-Control/Controller-Input-Handling/StateInterpreter.py) | Gamepad state | Command ID + normalized value |
| C | [Command Encoders](Packet/Command/UGV_Manual_Control_Commands/) | Command ID + value | 3-byte binary packet |
| D | [GCS XBee](Application/Infrastructure/GCSXBee.py) | Binary packet | Wireless radio transmission |

**Supported Commands:**

| Input | Command | ID | Data |
|-------|---------|----|----|
| Left Trigger (LT) | Velocity (reverse) | 6 | -100 to 0 |
| Right Trigger (RT) | Velocity (forward) | 6 | 0 to 100 |
| Left Stick X | Steering angle | 7 | -100 to 100 |
| Right Stick Y | Payload arm | 8 | -1 (down), 0 (stop), 1 (up) |
| X Button | End effector | 9 | 0 (open) or 1 (close) |

**Example:** Operator presses RT at 75% → command = `(ID:6, value:75)` → encoded to `b'\x01\x06\x4B'` → transmitted.

---

### **2. Command Reception at Vehicle**

| Stage | Component | Input | Output | Recipient |
|-------|-----------|-------|--------|----------|
| E | Vehicle XBee | Wireless radio packet | 3-byte binary | Command decoder |
| F | [Command Decoders](Packet/Command/UGV_Manual_Control_Commands/) | 3-byte binary | Decoded value (Python int/float) | Command queue |
| G | [Vehicle Infrastructure](Application/Infrastructure/VehicleXBee.py) | Decoded command | Queued command object | Your firmware |

**Firmware's Role:** 
- Call `ReceiveCommand()` to retrieve queued commands
- Convert command value to hardware protocol (CAN, SPI, PWM, GPIO, etc.)
- Send to motor controllers, servo drivers, and actuators

---

### **3. Telemetry Transmission Pipeline**

| Stage | Component | Input | Output |
|-------|-----------|-------|--------|
| H | XSens IMU/GPS | Continuous sensor measurement | ROS topic messages (100 Hz) |
| I | [ROS Sensor Driver](XSens/src/xsens_ros_mti_driver/) | Serial sensor data | Published ROS topics (/filter/positionlla, /filter/euler, /filter/velocity) |
| J | [XSens-to-GCS Bridge](XSens/src/xsens_ros_mti_driver/xsens_to_gcs_bridge.py) | ROS topic subscribers | 72-byte telemetry packet |
| K | [Vehicle XBee](Application/Infrastructure/VehicleXBee.py) | Telemetry packet | Wireless radio transmission |

**Telemetry Packet Contents (72 bytes):**
- Vehicle speed and orientation (pitch, roll, yaw)
- GPS position (latitude, longitude, altitude)
- Battery level, vehicle status
- Timestamp

---

### **4. Telemetry Reception at GCS**

| Stage | Component | Input | Output | Recipient |
|-------|-----------|-------|--------|----------|
| L | GCS XBee | Wireless radio packet | 72-byte binary | Telemetry decoder |
| M | [Telemetry Decoder](lib/gcs-packet/Packet/Telemetry/Telemetry.py) | 72-byte binary | Telemetry object with all fields | Display system |
| N | [GCS Infrastructure](Application/Infrastructure/GCSXBee.py) | Decoded telemetry | Queued telemetry object | GCS application |
| O | GCS Display/Dashboard | Telemetry object | Real-time vehicle data display | Operator |

---

## COMMUNICATION PROTOCOL

### **Physical Layer**
- **Radio Technology:** XBee 802.15.4 (IEEE 802.15.4 compliant)
- **Serial Connection:** UART at 115200 baud
- **Addressing:** 64-bit MAC addresses (e.g., `0013A200424353F7`)
- **Range:** ~100 meters line-of-sight typical

### **Data Format**
- **Encoding:** Binary struct packing (C-style format strings)
- **Command Packet:** 3 bytes minimum
  - Byte 0: Payload ID (always 1)
  - Byte 1: Command ID (1-9)
  - Byte 2+: Command data (normalized -100 to +100 or discrete 0-1)
- **Telemetry Packet:** Fixed 72 bytes
  - Fields: Speed, orientation (3 angles), position (lat/lon/alt), battery, status

### **Error Handling**
- XBee performs automatic CRC and retry at radio layer
- Telemetry packet size validation (72 bytes exactly)
- Command boundaries not currently enforced (firmware responsibility)

---

## TIMING & LATENCY

| Path | Typical Latency | Notes |
|------|-----------------|-------|
| Command (GCS → Firmware) | 15-50 ms | Wireless propagation varies with distance |
| Telemetry (Sensor → GCS) | 1-5 seconds | Configurable ROS bridge send rate (default 1 Hz) |
| End-to-End Round Trip | 2-10 seconds | Operator action → vehicle response visible on display |

---

## VEHICLE INTEGRATION POINTS

### **Your Firmware Responsibilities**

1. **Command Reception:**
   ```python
   from Application.Infrastructure.InfrastructureInterface import ReceiveCommand
   
   while True:
       cmd = ReceiveCommand()  # Blocks until GCS sends
       # Convert cmd.value to your hardware protocol
       # Send to motor controllers, servo drivers, etc.
   ```

2. **Hardware Interface:**
   - Map velocity commands (6) → motor PWM
   - Map steering commands (7) → servo angle
   - Map payload commands (8) → actuator position
   - Map end effector commands (9) → gripper state

3. **Telemetry Collection:** (Handled by XSens bridge; your firmware may contribute to battery/status reporting)

### **Configuration Required**

- Update GCS MAC address in [PacketLibrary.py](lib/gcs-packet/Packet/PacketLibrary/PacketLibrary.py)
- Set correct XBee serial port for vehicle
- Configure ROS bridge parameters (send_rate_hz, battery_life_default, etc.)

---

## DEPLOYMENT CHECKLIST

- [ ] XBee modules paired and configured
- [ ] MAC addresses stored in PacketLibrary
- [ ] Serial port permissions configured (Linux/macOS)
- [ ] Python venv created and dependencies installed
- [ ] ROS environment sourced (vehicle side)
- [ ] XSens sensor connected and calibrated
- [ ] Firmware command handler implemented
- [ ] Testing completed in lab before field deployment

---

## DATA FLOW SUMMARY

```
INBOUND (Operator Controls Vehicle):
Xbox Input → Controller Interpreter → Command Encoder 
  → GCS XBee TX → [WIRELESS] → Vehicle XBee RX 
  → Command Decoder → Queue → Your Firmware 
  → Hardware (motors, servos, actuators)

OUTBOUND (Sensor Data to Operator):
XSens Sensor → ROS Driver → Bridge Subscriber 
  → Telemetry Encoder → Vehicle XBee TX 
  → [WIRELESS] → GCS XBee RX 
  → Telemetry Decoder → Queue → GCS Display
```

---

## INTERFACES & PROTOCOLS

### **GCS-to-Vehicle Interface**
- Protocol: XBee 802.15.4 (binary frames)
- Bandwidth: ~10-100 commands/second theoretical
- Reliability: Best-effort (no ACK for manual control commands)

### **Vehicle-to-GCS Interface**
- Protocol: XBee 802.15.4 (binary frames)
- Data Rate: Configurable ROS bridge rate (default 1 Hz)
- Packet Size: Fixed 72 bytes per telemetry sample
- Reliability: Single transmission (no retries for telemetry)

### **Firmware Integration Interface**
- **Input:** `ReceiveCommand()` → Command object from queue
- **Output:** Device writes to hardware interfaces (CAN, SPI, PWM, etc.)
- **Synchronization:** Blocking queue calls (thread-safe Python primitives)

---

## RISK ASSESSMENT

| Risk | Mitigation |
|------|-----------|
| Radio link loss | Implement command timeout; stop vehicle after N missed heartbeats (firmware responsibility) |
| Corrupted data | XBee CRC + struct size validation; additional payload checksum recommended |
| Out-of-sync state | Periodic vehicle status heartbeat + manual reset capability |
| Firmware/Hardware timeout | Command watchdog in firmware; safe default (all-stop) on timeout |

---

## NEXT STEPS

1. **Firmware Team:** Implement command receiver and hardware interface (Section 2: Command Reception at Vehicle)
2. **Integration Testing:** Lab test all command types with actual motors/servos
3. **Telemetry Validation:** Confirm XSens data reaches GCS in real-time
4. **Field Testing:** Deploy to UGV and verify wireless range and latency under operational conditions
5. **Safety Review:** Verify emergency stop functionality and command bounds enforcement

---

**Document Version:** 1.0  
**Classification:** System Design Overview  
**Date:** March 20, 2026
