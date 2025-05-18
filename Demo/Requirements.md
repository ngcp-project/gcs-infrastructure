# GCS & Vehicle Data Transfer Requirements
# GCS

## Database
| Requirement | Description | Derives From |
| ----------- | ----------- | ------------ |
| DB-Software-01 | The Database SHALL send and receive commands from Vehicle Integration in JSON format. | |
| DB-Software-02 | The Database SHALL receive telemetry data from Vehicle Integration in JSON format. | |
| DB-Software-03 | The Database SHALL follow the data formatting as specified by DB/VI Data Transfer Formatting.

## Vehicle Integration & Infrastructure

| Requirement | Description | Derives From |
| ----------- | ----------- | ------------ |
| VI-Software-01 | Vehicle Integration SHALL send and receive commands from Database in JSON format. | | |
| VI-Software-02 | Vehicle Integration/Infrastructure SHALL transmit packetized commands to vehicles.
| VI-Software-03 | Vehicle Integration SHALL send telemetry data to Database in JSON format. | | |
| VI-Software-04 | Vehicle Integration/Infrastructure SHALL receive packetized telemetry data from the vehicles. | | |
| VI-Software-05 | Vehicle Integration/Infrastructure SHALL reformat packetized data to JSON data and JSON data to packetized data. | | | 
| VI-Software-06 | Communications with Database SHALL follow the data formatting as specified by GCS DB/VI Data Transfer Formatting..
| VI-Software-07 | Communications with vehicles SHALL follow the data formatting as specified by GCS VI/Infrastructure Data Transfer Formatting. | | |


## GCS DB/VI Data Transfer Formatting.
### Commands

### Telemetry

## GCS VI/Infrastructure Data Transfer Formatting.
### Commands

### Telemetry

# Vehicle
## Requirements
| Requirement | Description | Derives From |
| ----------- | ----------- | ------------ |
| Vehicle-01 | The vehicle SHALL receive user defined mission states and locations, search areas, keep in zones, and keep out zones from the GCS. | GCS-13 |
| Vehicle-02 | The vehicle SHALL respond to an emergency stop/loiter command from the GCS | GCS-14 |
| Vehicle-03 | The vehicle SHALL transmit telemetry data at a rate of at least 1 Hz. (1 transmission per second) | MRA-15, ERU-16, MEA-13, GCS-06, GCS-21 | 

According to the RFP, only the MRA needs to obey geofence boundaries? (MRA-08)

## Software Requirements
| Requirement | Description | Derives From |
| ----------- | ----------- | ------------ |
| V-Software-01 | The vehicle SHALL receive createMission, transitionNextStage, ~~getCamera~~, ~~getTelemetry~~, setEmergencyStop commands from the GCS.   |  |
| V-Software-02 | The vehicle SHOULD transmit an acknowledgment to confirm receipt of commands from the GCS. |  |
| V-Software-03 | The vehicle SHALL transmit telemetry data to the GCS. | |
| V-Software-04 | The vehicle SHALL follow the packet structures defined by the GCS. | |

### V-Software-01
#### createMission

#### transitionNextStage

#### setEmergencyStop

## Telemetry

## Commands
