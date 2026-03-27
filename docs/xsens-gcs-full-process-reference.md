# Xsens to GCS Full Process Reference

## 1) Purpose
This document explains the complete telemetry pipeline from Xsens sensor outputs to GCS telemetry consumption over XBee in this repository.

It covers:
- Folder and file ownership for the pipeline.
- Every function involved in the runtime path.
- Topic and message contracts.
- Threading and queue model.
- Build and runtime dependencies.
- Startup, shutdown, validation, and troubleshooting.
- Extension paths, including ROS2 options.

## 2) Repository Areas Involved

### Full top-level workspace folder inventory
- [Application](../Application)
- [Communication](../Communication)
- [Data Hub](../Data%20Hub)
- [Demo](../Demo)
- [FPV](../FPV)
- [Logger](../Logger)
- [TestScripts](../TestScripts)
- [UGV-Manual-Control](../UGV-Manual-Control)
- [XSens](../XSens)
- [docs](../docs)
- [lib](../lib)

### Top-level folders relevant to this flow
- Application: Python infrastructure API and XBee transport threads.
- XSens: ROS1 driver package and bridge script.
- Demo: legacy/demo sender/receiver scripts for manual testing.
- TestScripts: older interactive command and telemetry tests.
- docs: process and run documentation.
- lib: git submodules for packet and XBee libraries.

### Current critical dependency state
- lib/gcs-packet: expected to provide Telemetry and related packet classes.
- lib/xbee-python: expected to provide xbee transport implementation.
- Both are git submodules declared in [.gitmodules](../.gitmodules).

## 3) End-to-End Architecture

1. Xsens ROS node publishes sensor topics.
2. Bridge node subscribes to selected topics and stores latest values.
3. Bridge builds a Telemetry object at a configured rate.
4. Bridge enqueues telemetry via Infrastructure SendTelemetry.
5. Vehicle XBee telemetry thread dequeues, encodes, and transmits telemetry.
6. GCS XBee telemetry thread receives, decodes, enriches, and enqueues telemetry.
7. GCS app consumes telemetry via ReceiveTelemetry.

## 4) Data Flow Sequence (Detailed)

1. roslaunch starts xsens_mti_node and xsens_to_gcs_bridge.
2. xsens_mti_node creates XdaInterface and registers publishers based on YAML params.
3. Relevant publishers emit these topics:
- filter/positionlla
- filter/euler
- filter/velocity
- status
4. xsens_to_gcs_bridge subscribes to those topics.
5. Callback methods update a thread-safe state snapshot.
6. Bridge run loop periodically constructs a Telemetry packet object.
7. Bridge calls SendTelemetry, which pushes into TelemetryQueue.
8. VehicleXBee RunTelemetryThread blocks on TelemetryQueue.get().
9. VehicleXBee encodes Telemetry and transmits to GCS MAC.
10. GCSXBee RunTelemetryThread receives frame data and decodes Telemetry.
11. GCSXBee annotates Vehicle and MACAddress from sender address.
12. GCSXBee pushes decoded telemetry into TelemetryQueue.
13. GCS app calls ReceiveTelemetry to consume latest telemetry objects.

## 5) Folder and File Map

## Root and packaging
- [README.md](../README.md): setup and interface usage notes.
- [requirements.txt](../requirements.txt): editable installs for submodules.
- [pyproject.toml](../pyproject.toml): package metadata for Application package discovery.
- [.gitmodules](../.gitmodules): declares gcs-packet and xbee-python submodules.

## Infrastructure package
- [Application/__init__.py](../Application/__init__.py)
- [Application/Infrastructure/__init__.py](../Application/Infrastructure/__init__.py): exports public infrastructure API.
- [Application/Infrastructure/PacketQueue.py](../Application/Infrastructure/PacketQueue.py): defines global queues.
- [Application/Infrastructure/InfrastructureInterface.py](../Application/Infrastructure/InfrastructureInterface.py): top-level API methods.
- [Application/Infrastructure/VehicleXBee.py](../Application/Infrastructure/VehicleXBee.py): vehicle-side send/receive threads.
- [Application/Infrastructure/GCSXBee.py](../Application/Infrastructure/GCSXBee.py): GCS-side send/receive threads.

## Xsens ROS package
- [XSens/src/xsens_ros_mti_driver/package.xml](../XSens/src/xsens_ros_mti_driver/package.xml): ROS package dependencies.
- [XSens/src/xsens_ros_mti_driver/CMakeLists.txt](../XSens/src/xsens_ros_mti_driver/CMakeLists.txt): build and install targets.
- [XSens/src/xsens_ros_mti_driver/src/main.cpp](../XSens/src/xsens_ros_mti_driver/src/main.cpp): xsens_mti_node entry point.
- [XSens/src/xsens_ros_mti_driver/include/xdainterface.h](../XSens/src/xsens_ros_mti_driver/include/xdainterface.h): XdaInterface API.
- [XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp](../XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp): sensor connection/config/publish flow.
- [XSens/src/xsens_ros_mti_driver/msg/XsStatusWord.msg](../XSens/src/xsens_ros_mti_driver/msg/XsStatusWord.msg): status message schema.
- [XSens/src/xsens_ros_mti_driver/param/xsens_mti_node.yaml](../XSens/src/xsens_ros_mti_driver/param/xsens_mti_node.yaml): output and device config.
- [XSens/src/xsens_ros_mti_driver/launch/xsens_mti_node.launch](../XSens/src/xsens_ros_mti_driver/launch/xsens_mti_node.launch): starts driver node.
- [XSens/src/xsens_ros_mti_driver/launch/xsens_mti_with_gcs_bridge.launch](../XSens/src/xsens_ros_mti_driver/launch/xsens_mti_with_gcs_bridge.launch): starts driver + bridge.
- [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py): core bridge node.

## Message publishers directly used by bridge topics
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/positionllapublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/positionllapublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/orientationeulerpublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/orientationeulerpublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/velocitypublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/velocitypublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/statuspublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/statuspublisher.h)

## Complete messagepublishers folder inventory
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/accelerationhrpublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/accelerationhrpublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/accelerationpublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/accelerationpublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/angularvelocityhrpublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/angularvelocityhrpublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/angularvelocitypublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/angularvelocitypublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/freeaccelerationpublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/freeaccelerationpublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/gnssposepublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/gnssposepublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/gnsspublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/gnsspublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/imupublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/imupublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/magneticfieldpublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/magneticfieldpublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/nmeapublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/nmeapublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/orientationeulerpublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/orientationeulerpublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/orientationincrementspublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/orientationincrementspublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/orientationpublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/orientationpublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/packetcallback.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/packetcallback.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/positionllapublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/positionllapublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/pressurepublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/pressurepublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/publisherhelperfunctions.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/publisherhelperfunctions.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/statuspublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/statuspublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/temperaturepublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/temperaturepublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/timereferencepublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/timereferencepublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/transformpublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/transformpublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/twistpublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/twistpublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/utctimepublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/utctimepublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/velocityincrementpublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/velocityincrementpublisher.h)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers/velocitypublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/velocitypublisher.h)

## Related validation scripts
- [Demo/vehicle.py](../Demo/vehicle.py): synthetic telemetry sender over XBee.
- [Demo/GCS.py](../Demo/GCS.py): telemetry receiver demo over XBee.
- [TestScripts/TelemetryTransmitTest.py](../TestScripts/TelemetryTransmitTest.py): older telemetry send test.
- [TestScripts/CommandTransmitTest.py](../TestScripts/CommandTransmitTest.py): older command send/receive test.

### Function map for demo and test scripts

Demo/GCS:
- manage_serial at [Demo/GCS.py](../Demo/GCS.py#L21)
- listen_keyboard at [Demo/GCS.py](../Demo/GCS.py#L44)
- main at [Demo/GCS.py](../Demo/GCS.py#L54)

Demo/vehicle:
- update_telemetry_data at [Demo/vehicle.py](../Demo/vehicle.py#L25)
- update_telemetry at [Demo/vehicle.py](../Demo/vehicle.py#L45)
- send_telemetry at [Demo/vehicle.py](../Demo/vehicle.py#L108)
- main at [Demo/vehicle.py](../Demo/vehicle.py#L126)

TestScripts/TelemetryTransmitTest:
- main at [TestScripts/TelemetryTransmitTest.py](../TestScripts/TelemetryTransmitTest.py#L28)
- ListenForData at [TestScripts/TelemetryTransmitTest.py](../TestScripts/TelemetryTransmitTest.py#L75)

TestScripts/CommandTransmitTest:
- main at [TestScripts/CommandTransmitTest.py](../TestScripts/CommandTransmitTest.py#L19)
- ProcessCommand at [TestScripts/CommandTransmitTest.py](../TestScripts/CommandTransmitTest.py#L80)
- HeartbeatCommand at [TestScripts/CommandTransmitTest.py](../TestScripts/CommandTransmitTest.py#L90)
- KeepInCommand at [TestScripts/CommandTransmitTest.py](../TestScripts/CommandTransmitTest.py#L103)
- EmergencyStopCommand at [TestScripts/CommandTransmitTest.py](../TestScripts/CommandTransmitTest.py#L131)
- ListenForData at [TestScripts/CommandTransmitTest.py](../TestScripts/CommandTransmitTest.py#L144)

## Existing docs
- [docs/xsens-to-gcs-send-data.md](./xsens-to-gcs-send-data.md)
- [docs/gcs-receive-data.md](./gcs-receive-data.md)
- [docs/run-commands.md](./run-commands.md)
- [docs/gcs-xsens-wrap-up.md](./gcs-xsens-wrap-up.md)

## 6) Function-by-Function Reference

### Infrastructure API: InfrastructureInterface
Source: [Application/Infrastructure/InfrastructureInterface.py](../Application/Infrastructure/InfrastructureInterface.py)

- LaunchGCSXBee at [Application/Infrastructure/InfrastructureInterface.py](../Application/Infrastructure/InfrastructureInterface.py#L8)
Role: starts GCS-side XBee subsystem by delegating to StartGCSXBee.

- LaunchVehicleXBee at [Application/Infrastructure/InfrastructureInterface.py](../Application/Infrastructure/InfrastructureInterface.py#L11)
Role: starts vehicle-side XBee subsystem by delegating to StartVehicleXBee.

- SendCommand at [Application/Infrastructure/InfrastructureInterface.py](../Application/Infrastructure/InfrastructureInterface.py#L14)
Role: sets destination vehicle and queues command to CommandQueue.

- SendTelemetry at [Application/Infrastructure/InfrastructureInterface.py](../Application/Infrastructure/InfrastructureInterface.py#L21)
Role: queues telemetry object to TelemetryQueue for transmission.

- ReceiveCommand at [Application/Infrastructure/InfrastructureInterface.py](../Application/Infrastructure/InfrastructureInterface.py#L26)
Role: blocks until a command is available from CommandQueue, returns command.

- ReceiveTelemetry at [Application/Infrastructure/InfrastructureInterface.py](../Application/Infrastructure/InfrastructureInterface.py#L35)
Role: blocks until telemetry is available from TelemetryQueue, returns telemetry.

### Vehicle transport: VehicleXBee
Source: [Application/Infrastructure/VehicleXBee.py](../Application/Infrastructure/VehicleXBee.py)

- StartVehicleXBee at [Application/Infrastructure/VehicleXBee.py](../Application/Infrastructure/VehicleXBee.py#L16)
Role: opens serial XBee, starts command and telemetry worker threads.

- RunCommandThread at [Application/Infrastructure/VehicleXBee.py](../Application/Infrastructure/VehicleXBee.py#L35)
Role: receives inbound command packets from radio and decodes command IDs 1 through 6.

- RunTelemetryThread at [Application/Infrastructure/VehicleXBee.py](../Application/Infrastructure/VehicleXBee.py#L71)
Role: pulls Telemetry objects from queue, encodes, transmits to GCS MAC address.

### GCS transport: GCSXBee
Source: [Application/Infrastructure/GCSXBee.py](../Application/Infrastructure/GCSXBee.py)

- StartGCSXBee at [Application/Infrastructure/GCSXBee.py](../Application/Infrastructure/GCSXBee.py#L16)
Role: opens serial XBee, starts outbound command sender and inbound telemetry receiver threads.

- RunCommandThread at [Application/Infrastructure/GCSXBee.py](../Application/Infrastructure/GCSXBee.py#L35)
Role: sends queued commands to one or multiple vehicle MAC addresses.

- RunTelemetryThread at [Application/Infrastructure/GCSXBee.py](../Application/Infrastructure/GCSXBee.py#L68)
Role: receives frames, decodes Telemetry, annotates sender metadata, queues for app consumption.

### Shared queue definitions
Source: [Application/Infrastructure/PacketQueue.py](../Application/Infrastructure/PacketQueue.py)

- CommandQueue: unbounded Queue instance.
- TelemetryQueue: unbounded Queue instance.

### Bridge node: xsens_to_gcs_bridge
Source: [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py)

Top-level helper functions:
- _prepend_if_dir at [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py#L22)
Role: add existing directories to Python path.

- _bootstrap_import_paths at [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py#L28)
Role: discover repository roots and add Application and submodule paths.

Class XsensTelemetryState at [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py#L89)
Methods:
- __init__ at [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py#L92)
- update_euler at [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py#L103)
- update_position at [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py#L109)
- update_velocity at [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py#L116)
- update_status at [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py#L123)
- snapshot at [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py#L128)

Class XsensToGcsBridge at [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py#L142)
Methods:
- __init__ at [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py#L145)
- _build_telemetry at [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py#L171)
- run at [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py#L192)

Entry point:
- main at [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py#L203)
Role: initializes ROS node, validates xbee_port param, starts VehicleXBee, starts bridge loop.

### Xsens node entrypoint
Source: [XSens/src/xsens_ros_mti_driver/src/main.cpp](../XSens/src/xsens_ros_mti_driver/src/main.cpp)

- main at [XSens/src/xsens_ros_mti_driver/src/main.cpp](../XSens/src/xsens_ros_mti_driver/src/main.cpp#L45)
Role:
1. Initialize ROS node.
2. Construct XdaInterface.
3. connectDevice.
4. registerPublishers.
5. prepare.
6. spin loop.

### XdaInterface methods
Source: [XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp](../XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp)

- Constructor at [XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp](../XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp#L75)
- spinFor at [XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp](../XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp#L93)
- registerPublishers at [XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp](../XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp#L106)
- connectDevice at [XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp](../XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp#L231)
- prepare at [XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp](../XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp#L392)
- manualGyroBiasEstimation at [XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp](../XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp#L463)
- setupManualGyroBiasEstimation at [XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp](../XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp#L494)
- rtcmCallback at [XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp](../XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp#L548)
- close at [XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp](../XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp#L557)
- registerCallback at [XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp](../XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp#L568)
- handleError at [XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp](../XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp#L573)
- configureSensorSettings at [XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp](../XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp#L586)

## 7) Topic and Message Contracts

### Topics consumed by bridge
- position topic: default filter/positionlla, type geometry_msgs/Vector3Stamped.
- euler topic: default filter/euler, type geometry_msgs/Vector3Stamped.
- velocity topic: default filter/velocity, type geometry_msgs/Vector3Stamped.
- status topic: default status, type xsens_mti_driver/XsStatusWord.

Topic defaults are defined in [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py#L155).

### Where those topics are published
- positionlla publisher advertise call at [XSens/src/xsens_ros_mti_driver/src/messagepublishers/positionllapublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/positionllapublisher.h#L49)
- euler publisher advertise call at [XSens/src/xsens_ros_mti_driver/src/messagepublishers/orientationeulerpublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/orientationeulerpublisher.h#L49)
- velocity publisher advertise call at [XSens/src/xsens_ros_mti_driver/src/messagepublishers/velocitypublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/velocitypublisher.h#L49)
- status publisher advertise call at [XSens/src/xsens_ros_mti_driver/src/messagepublishers/statuspublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/statuspublisher.h#L47)

### Status field mapping used by bridge
- gnss_fix bit parsed in status publisher at [XSens/src/xsens_ros_mti_driver/src/messagepublishers/statuspublisher.h](../XSens/src/xsens_ros_mti_driver/src/messagepublishers/statuspublisher.h#L61)
- bridge maps gnss_fix to vehicle_status at [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py#L126)

## 8) Telemetry Field Mapping in Bridge

Bridge mapping occurs in _build_telemetry at [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py#L171).

- Telemetry.speed = sqrt(vx^2 + vy^2 + vz^2)
- Telemetry.pitch = euler.y
- Telemetry.yaw = euler.z
- Telemetry.roll = euler.x
- Telemetry.altitude = positionlla.z
- Telemetry.current_latitude = positionlla.x
- Telemetry.current_longitude = positionlla.y
- Telemetry.vehicle_status = int(status.gnss_fix)
- Telemetry.patient_status = configured default
- Telemetry.message_flag = configured default
- Telemetry.message_lat = configured default
- Telemetry.message_lon = configured default
- Telemetry.battery_life = configured default
- Telemetry.last_updated = epoch seconds from time.time

## 9) Launch and Runtime Wiring

### Combined launch
Source: [XSens/src/xsens_ros_mti_driver/launch/xsens_mti_with_gcs_bridge.launch](../XSens/src/xsens_ros_mti_driver/launch/xsens_mti_with_gcs_bridge.launch)

What it does:
1. Declares private params for bridge runtime.
2. Includes xsens_mti_node.launch.
3. Starts bridge script node in package xsens_mti_driver.

### Driver launch
Source: [XSens/src/xsens_ros_mti_driver/launch/xsens_mti_node.launch](../XSens/src/xsens_ros_mti_driver/launch/xsens_mti_node.launch)

What it does:
- Starts xsens_mti_node and loads parameter file xsens_mti_node.yaml.

### Param defaults relevant to this pipeline
Source: [XSens/src/xsens_ros_mti_driver/param/xsens_mti_node.yaml](../XSens/src/xsens_ros_mti_driver/param/xsens_mti_node.yaml)

- pub_euler true at [XSens/src/xsens_ros_mti_driver/param/xsens_mti_node.yaml](../XSens/src/xsens_ros_mti_driver/param/xsens_mti_node.yaml#L139)
- pub_status true at [XSens/src/xsens_ros_mti_driver/param/xsens_mti_node.yaml](../XSens/src/xsens_ros_mti_driver/param/xsens_mti_node.yaml#L151)
- pub_positionLLA true at [XSens/src/xsens_ros_mti_driver/param/xsens_mti_node.yaml](../XSens/src/xsens_ros_mti_driver/param/xsens_mti_node.yaml#L154)
- pub_velocity true at [XSens/src/xsens_ros_mti_driver/param/xsens_mti_node.yaml](../XSens/src/xsens_ros_mti_driver/param/xsens_mti_node.yaml#L155)
- output_data_rate default 100 at [XSens/src/xsens_ros_mti_driver/param/xsens_mti_node.yaml](../XSens/src/xsens_ros_mti_driver/param/xsens_mti_node.yaml#L167)

## 10) Threading and Queue Model

### Vehicle-side process (bridge process)
Threads:
- bridge main loop thread: builds telemetry and queues it.
- VehicleXBee command thread: listens for incoming commands.
- VehicleXBee telemetry thread: dequeues telemetry and transmits.

Queue:
- TelemetryQueue used producer/consumer style.

### GCS-side process
Threads:
- GCS command sender thread: sends commands queued by application.
- GCS telemetry receiver thread: receives telemetry and queues it.

Queue:
- TelemetryQueue used for decoded telemetry handoff to app layer.

## 11) Build and Dependency Chain

### Python side
- [requirements.txt](../requirements.txt) installs editable submodules.
- Bridge imports Infrastructure package and Telemetry package.
- Bridge path bootstrapping attempts to resolve local source-tree imports.

### ROS side
- [XSens/src/xsens_ros_mti_driver/package.xml](../XSens/src/xsens_ros_mti_driver/package.xml) declares ROS deps.
- [XSens/src/xsens_ros_mti_driver/CMakeLists.txt](../XSens/src/xsens_ros_mti_driver/CMakeLists.txt) builds C++ node and installs bridge script.
- CMake ExternalProject builds xspublic.

### Critical external libs
- gcs-packet: Telemetry encode/decode implementation.
- xbee-python: XBee serial transport implementation.

## 12) Runtime Parameters (Bridge)

Defined in [XSens/src/xsens_ros_mti_driver/launch/xsens_mti_with_gcs_bridge.launch](../XSens/src/xsens_ros_mti_driver/launch/xsens_mti_with_gcs_bridge.launch)
and consumed in [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py).

Required:
- xbee_port

Optional:
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

## 13) Startup and Shutdown Semantics

### Recommended startup order
1. Start GCS receiver process and call LaunchGCSXBee.
2. Start Xsens + bridge launch on vehicle side.
3. Confirm ROS topics and GCS telemetry consumption.

### Shutdown
- Ctrl+C bridge launch first, then GCS process.
- Internal loops terminate when ROS shutdown occurs or serial object closes.

## 14) Validation Checklist

- Submodules initialized and installed.
- ROS workspace built and sourced.
- Correct serial ports selected for both XBee devices.
- filter/positionlla, filter/euler, filter/velocity, and status are visible in rostopic list.
- Bridge logs subscribed topics and starts VehicleXBee.
- GCS ReceiveTelemetry loop shows decoded telemetry objects.

## 15) Common Failure Modes and Diagnostics

### Import errors in bridge process
Symptoms:
- ImportError for Infrastructure, Telemetry, or xbee modules.

Checks:
- Confirm submodules exist under lib.
- Confirm pip install from requirements completed in active environment.
- Set GCS_INFRASTRUCTURE_ROOT to repository root.

### No telemetry on GCS
Checks:
- Verify bridge is running and not crashing after startup.
- Verify vehicle XBee can transmit and GCS XBee port is correct.
- Verify PacketLibrary MAC mapping in packet library matches your hardware addresses.

### ROS topics missing
Checks:
- Verify xsens_mti_node launched.
- Verify YAML pub flags are true.
- Verify sensor is connected and outputting required data groups.

### Throughput mismatch
Checks:
- Xsens output_data_rate can be high, while send_rate_hz controls bridge transmit cadence.
- Tune send_rate_hz for radio bandwidth and desired update rate.

## 16) ROS1 and ROS2 Options

Current implementation is ROS1 (rospy + catkin).

To keep existing transport and move toward ROS2 you have two main options:
- Use ros1_bridge between ROS2 sensor graph and this ROS1 bridge.
- Reimplement xsens_to_gcs_bridge.py in rclpy while preserving Infrastructure interface contract.

If choosing ROS2 rewrite, keep these invariants:
- Same Telemetry field mapping.
- Same send cadence behavior.
- Same LaunchVehicleXBee call pattern.
- Same queue handoff to VehicleXBee threads.

## 17) Important Notes and Constraints

- LaunchGCSXBee and LaunchVehicleXBee should not be used together in the same process.
- Infrastructure threads are long-running and designed around blocking queue operations.
- Telemetry encode/decode details are owned by external gcs-packet dependency.
- XBee serial behavior is owned by external xbee-python dependency.

## 18) Quick Navigation Index

### Most important files to read first
1. [XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py](../XSens/src/xsens_ros_mti_driver/scripts/xsens_to_gcs_bridge.py)
2. [Application/Infrastructure/InfrastructureInterface.py](../Application/Infrastructure/InfrastructureInterface.py)
3. [Application/Infrastructure/VehicleXBee.py](../Application/Infrastructure/VehicleXBee.py)
4. [Application/Infrastructure/GCSXBee.py](../Application/Infrastructure/GCSXBee.py)
5. [XSens/src/xsens_ros_mti_driver/launch/xsens_mti_with_gcs_bridge.launch](../XSens/src/xsens_ros_mti_driver/launch/xsens_mti_with_gcs_bridge.launch)
6. [XSens/src/xsens_ros_mti_driver/param/xsens_mti_node.yaml](../XSens/src/xsens_ros_mti_driver/param/xsens_mti_node.yaml)

### Supporting internals
- [XSens/src/xsens_ros_mti_driver/src/main.cpp](../XSens/src/xsens_ros_mti_driver/src/main.cpp)
- [XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp](../XSens/src/xsens_ros_mti_driver/src/xdainterface.cpp)
- [XSens/src/xsens_ros_mti_driver/msg/XsStatusWord.msg](../XSens/src/xsens_ros_mti_driver/msg/XsStatusWord.msg)
- [XSens/src/xsens_ros_mti_driver/src/messagepublishers](../XSens/src/xsens_ros_mti_driver/src/messagepublishers)
