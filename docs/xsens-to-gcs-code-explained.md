# Xsens to GCS Telemetry: Code Walkthrough

## Goal of this document
Explain exactly how telemetry leaves Xsens, flows through xsens_to_gcs_bridge.py, and is transmitted to GCS over XBee.

This is a code-level explanation focused on:
- [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py)
- Supporting transport files that actually deliver telemetry to GCS.

## High-level pipeline
1. Xsens driver publishes ROS topics.
2. Bridge subscribes to those topics and stores latest values.
3. Bridge creates a Telemetry object on a timer.
4. Bridge calls SendTelemetry.
5. VehicleXBee thread dequeues, encodes, and transmits telemetry to GCS MAC.

Core send path files:
- [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py)
- [Application/Infrastructure/InfrastructureInterface.py](../Application/Infrastructure/InfrastructureInterface.py)
- [Application/Infrastructure/PacketQueue.py](../Application/Infrastructure/PacketQueue.py)
- [Application/Infrastructure/VehicleXBee.py](../Application/Infrastructure/VehicleXBee.py)

Related topic source files:
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/positionllapublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/positionllapublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/orientationeulerpublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/orientationeulerpublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/velocitypublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/velocitypublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/statuspublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/statuspublisher.h)

Launch wiring:
- [XSens/src/xsens_ros_mti_driver/launch/xsens_mti_with_gcs_bridge.launch](../XSens/src/xsens_ros_mti_driver/launch/xsens_mti_with_gcs_bridge.launch)

## Part 1: xsens_to_gcs_bridge.py method-by-method
Source file:
- [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py)

### _prepend_if_dir(path) at line 22
What it does:
- If a directory exists and is not already in sys.path, prepends it.

Why it matters:
- The bridge depends on local modules from this repo and submodules.
- This helper safely prepares Python import paths.

### _bootstrap_import_paths() at line 28
What it does:
- Collects candidate roots from:
- GCS_INFRASTRUCTURE_ROOT environment variable.
- Current working directory.
- Current script directory and up to 8 ancestors.
- De-duplicates those roots.
- Adds these directories to sys.path when present:
- Application
- lib/gcs-packet
- lib/gcs-packet/Packet
- lib/gcs-packet/Application
- lib/xbee-python
- lib/xbee-python/src

Why it matters:
- The script can run from source or catkin devel wrappers.
- This prevents import failures when execution path changes.

### Import block after ATTEMPTED_ROOTS
What it does:
- Imports LaunchVehicleXBee and SendTelemetry from Infrastructure.
- Imports Telemetry from `Telemetry.Telemetry` (so it matches `VehicleXBee`'s `isinstance` checks).

Why it matters:
- Uses the actual `gcs-packet` module path, avoiding redundant/unused import fallbacks.

### class XsensTelemetryState at line 89
Purpose:
- Thread-safe container for latest ROS topic values.

#### __init__ at line 92
Initializes:
- roll, pitch, yaw
- speed
- latitude, longitude, altitude
- vehicle_status
- lock for synchronized read/write

#### update_euler(msg) at line 106
Input:
- geometry_msgs/Vector3Stamped from filter/euler

Behavior:
- Stores x->roll, y->pitch, z->yaw under lock.

#### update_position(msg) at line 112
Input:
- geometry_msgs/Vector3Stamped from filter/positionlla

Behavior:
- Stores x->latitude, y->longitude, z->altitude under lock.

#### update_velocity(msg) at line 116
Input:
- geometry_msgs/Vector3Stamped from filter/velocity

Behavior:
- Computes speed as sqrt(vx^2 + vy^2 + vz^2).
- Stores speed under lock.

#### update_status(msg) at line 123
Input:
- xsens_mti_driver/XsStatusWord from status topic

Behavior:
- Sets vehicle_status to 1 when gnss_fix is true, else 0.

#### snapshot() at line 128
Behavior:
- Returns atomic snapshot dictionary of current state.

Why this class design matters:
- ROS callbacks happen asynchronously.
- Bridge send loop needs coherent values without races.

### class XsensToGcsBridge at line 142
Purpose:
- Reads parameters, subscribes to topics, builds telemetry packets, and sends them.

#### __init__ at line 145
Reads params:
- send_rate_hz
- battery_life_default
- patient_status_default
- message_flag_default
- message_lat_default
- message_lon_default
- position_topic
- euler_topic
- velocity_topic
- status_topic

Subscribes to topics:
- position_topic -> update_position
- euler_topic -> update_euler
- velocity_topic -> update_velocity
- status_topic -> update_status

#### _build_telemetry() at line 171
Behavior:
- Pulls snapshot from XsensTelemetryState.
- Creates Telemetry object.
- Maps fields:
- Speed, Pitch, Yaw, Roll, Altitude
- CurrentPositionX/CurrentPositionY from latitude/longitude
- VehicleStatus
- BatteryLife, PatientStatus, MessageFlag, MessageLat, MessageLon from defaults
- LastUpdated set with `int(time.time())`
- Returns Telemetry instance.

#### run() at line 192
Behavior:
- Validates send_rate_hz > 0.
- Computes period = 1/send_rate_hz.
- Loop until ROS shutdown:
- build telemetry
- SendTelemetry(telemetry)
- sleep(period)

Key point:
- run() does not directly talk to serial or XBee.
- It only queues telemetry via SendTelemetry.

### main() at line 203
Behavior:
- Initializes ROS node xsens_to_gcs_bridge.
- Reads required private param xbee_port.
- Starts vehicle-side XBee subsystem via LaunchVehicleXBee(xbee_port).
- Creates XsensToGcsBridge and starts run loop.

Key point:
- main() starts both:
- telemetry producer (bridge loop)
- telemetry transport worker threads (via LaunchVehicleXBee)

## Part 2: Files that actually send telemetry to GCS

### InfrastructureInterface.py
Source:
- [Application/Infrastructure/InfrastructureInterface.py](../Application/Infrastructure/InfrastructureInterface.py)

Relevant methods:
- LaunchVehicleXBee at line 11
- SendTelemetry at line 21

How bridge uses it:
- main() calls LaunchVehicleXBee.
- run() calls SendTelemetry.

What SendTelemetry really does:
- Pushes Telemetry instance into TelemetryQueue.

### PacketQueue.py
Source:
- [Application/Infrastructure/PacketQueue.py](../Application/Infrastructure/PacketQueue.py)

Defines shared queues:
- CommandQueue
- TelemetryQueue

Why it matters:
- Decouples data production from serial transmission.
- Bridge can run at fixed rate while transport thread blocks independently.

### VehicleXBee.py
Source:
- [Application/Infrastructure/VehicleXBee.py](../Application/Infrastructure/VehicleXBee.py)

Relevant methods:
- StartVehicleXBee at line 16
- RunTelemetryThread at line 71

How telemetry is transmitted:
1. StartVehicleXBee opens XBee serial connection.
2. Starts RunTelemetryThread.
3. RunTelemetryThread blocks on TelemetryQueue.get().
4. Validates object is Telemetry.
5. Encodes packet using TelemetryInstance.Encode().
6. Sends with xbee.transmit_data(encoded, PacketLibrary.GetGCSMACAddress()).

This is the exact step where bytes leave vehicle and go to GCS over radio.

## Part 3: Where bridge topics come from

### position topic source
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/positionllapublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/positionllapublisher.h)

Publishes:
- filter/positionlla as geometry_msgs/Vector3Stamped
- x=latitude, y=longitude, z=altitude

### euler topic source
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/orientationeulerpublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/orientationeulerpublisher.h)

Publishes:
- filter/euler as geometry_msgs/Vector3Stamped
- x=roll, y=pitch, z=yaw

### velocity topic source
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/velocitypublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/velocitypublisher.h)

Publishes:
- filter/velocity as geometry_msgs/Vector3Stamped
- x,y,z velocity components

### status topic source
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/statuspublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/statuspublisher.h)

Publishes:
- status as xsens_mti_driver/XsStatusWord

Bridge uses:
- gnss_fix field to derive vehicle_status

## Part 4: Launch file integration
Source:
- [XSens/src/xsens_ros_mti_driver/launch/xsens_mti_with_gcs_bridge.launch](../XSens/src/xsens_ros_mti_driver/launch/xsens_mti_with_gcs_bridge.launch)

What this launch file does:
1. Defines bridge params and topic names.
2. Includes xsens_mti_node.launch (starts Xsens ROS driver).
3. Starts xsens_to_gcs_bridge.py node.

Why this matters:
- One command brings up both data source and bridge sender.

## Part 5: End-to-end call trace

1. ROS callback updates state:
- update_position / update_euler / update_velocity / update_status
2. run loop calls _build_telemetry
3. run loop calls SendTelemetry
4. SendTelemetry enqueues to TelemetryQueue
5. RunTelemetryThread dequeues
6. Telemetry.Encode
7. xbee.transmit_data(..., GCS_MAC)

## Part 6: Supporting receive-side file (for completeness)
Even though your question is about sending, this file closes the loop on GCS side:
- [Application/Infrastructure/GCSXBee.py](../Application/Infrastructure/GCSXBee.py)

Relevant method:
- RunTelemetryThread

Behavior:
- retrieve_data from GCS XBee
- Telemetry.Decode on payload
- annotate sender Vehicle and MACAddress
- enqueue decoded telemetry for app consumption

## Part 7: Easy mental model
Think of the system as 3 layers:

1. Sensor layer (ROS topics)
- Xsens publishes raw navigation status/state.

2. Translation layer (bridge)
- Converts ROS topic values into your project Telemetry packet schema.

3. Transport layer (Infrastructure/VehicleXBee)
- Encodes Telemetry and sends bytes over XBee to GCS.

This separation is good because:
- You can change sensor source without rewriting XBee transport.
- You can change transport without rewriting sensor callbacks.

## Part 8: Common places to modify behavior

If you want to change topic names or rate:
- [XSens/src/xsens_ros_mti_driver/launch/xsens_mti_with_gcs_bridge.launch](../XSens/src/xsens_ros_mti_driver/launch/xsens_mti_with_gcs_bridge.launch)

If you want to change field mapping logic:
- _build_telemetry in [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py)

If you want to change how status maps to vehicle_status:
- update_status in [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py)

If you want to change destination MAC behavior:
- RunTelemetryThread in [Application/Infrastructure/VehicleXBee.py](../Application/Infrastructure/VehicleXBee.py)

## Part 9: Important behavior notes
- send_rate_hz must be greater than 0.
- xbee_port is required and bridge exits if missing.
- SendTelemetry currently prints Command Queued (wording from infrastructure file).
- Bridge imports depend on submodules or installed packages being available.

## Part 10: Quick run checklist
1. Initialize submodules and install requirements.
2. Build and source ROS workspace.
3. Launch GCS receiver process.
4. Start xsens_mti_with_gcs_bridge.launch with correct xbee_port.
5. Confirm telemetry appears on GCS side.
