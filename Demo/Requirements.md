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

#### createMission (DB to VI)
```json
// TODO
{

}
```

#### transitionNextStage (DB to VI)
```json
// TODO
{

}
```
#### ~~getCamera~~
#### ~~getTelemetry~~
#### setEmergencyStop (DB to VI)
```json
// TODO
{

}
```
### Telemetry (VI to Database)
```json
{
  "Speed": float,
  "Pitch": float,
  "Yaw": float,
  "Roll": float,
  "Altitude": float,
  "BatteryLife": float,
  "LastUpdated": double, // epoch time
  "CurrentPosition": {
    "Latitude": double,
    "Longitude": double
  },
  "VehicleStatus": string,
//   "MessageInfo": object,
//   "PatientStatus": string,
  "patientLocation": {
    "Latitude": double,
    "Longitude": double
  }
  "packageLocation": {
    "Latitude": double,
    "Longitude": double
  }
}
```
## GCS VI/Infrastructure Data Transfer Formatting.
### Commands
#### createMission (VI to Vehicle)
```
// TODO

```

#### transitionNextStage (VI to Vehicle)
```
// TODO
```
#### ~~getCamera~~
#### ~~getTelemetry~~
#### setEmergencyStop (VI to Vehicle)
```
// TODO

```

#### Command Response (Vehicle to VI)

### Telemetry (Vehicle to VI)
# Vehicle Telemetry Payload Structure

| Field             | Type                   | Num Bytes | End Byte | Byte Range     |
|------------------|------------------------|-----------|----------|----------------|
| payloadId        | int                    | 1         | 1        | 0 - 1          |
| speed (ft/s)     | float                  | 4         | 5        | 1 - 5          |
| pitch (º)        | float                  | 4         | 9        | 5 - 9          |
| yaw (º)          | float                  | 4         | 13       | 9 - 13         |
| roll (º)         | float                  | 4         | 17       | 13 - 17        |
| altitude (ft)    | float                  | 4         | 21       | 17 - 21        |
| batteryLife      | float                  | 4         | 25       | 21 - 25        |
| lastUpdated      | unsigned long long     | 8         | 33       | 25 - 33        |
| currentPosition  | (double, double)       | 16        | 49       | 33 - 49        |
| vehicleStatus    | int                    | 1         | 50       | 49 - 50        |
| patientLocation  | (double, double)       | 16        | 66       | 50 - 66        |
| packageLocation  | (double, double)       | 16        | 82       | 66 - 82        |

**Total Bytes:** 82

> [!NOTE]
> Will be implemeted by `Telemetry.py` (Needs to be updated) <br>
> Path: `gcs-infrastructure/Packet/Telemetry/Telemetry.py`


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
