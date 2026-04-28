from Command import *
from Enum import *
from Infrastructure.InfrastructureInterface import *
from PacketLibrary.PacketLibrary import PacketLibrary
from Telemetry.Telemetry import Telemetry

# Only relevant to the test script
import ast
# --------------------------------

PORT = "COM4"

# This is an example script and should be copied and pasted into your repository where you have gcs-infrastructure as a git submodule

# Read gcs-infrastructure documentation to understand the implications of the following function calls

PacketLibrary.SetVehicleMACAddress(Vehicle.MRA, "0013A200428396C0")

LaunchGCSXBee(PORT)

KeepInCoordinates = [[0, 4], [4, 0], [4, 4], [0, 4]]

Command1 = Heartbeat(ConnectionStatus.Connected)
Command2 = EmergencyStop(0)
Command3 = AddZone(ZoneType.KeepIn, KeepInCoordinates)

SendCommand(Command1, Vehicle.MRA)
SendCommand(Command2, Vehicle.MRA)
SendCommand(Command3, Vehicle.MRA)

Telemetry1 = None
Telemetry2 = None
Telemetry3 = None

while True:
    if (Telemetry1 is None):
        Telemetry1 = ReceiveTelemetry(False)

        continue

    if (Telemetry2 is None):
        Telemetry2 = ReceiveTelemetry(False)

        continue

    if (Telemetry3 is None):
        Telemetry3 = ReceiveTelemetry(False)

        continue

    if ((Telemetry1 != None) and (Telemetry2 != None) and (Telemetry3 != None)):
        print(f"MAC Address of {Telemetry1.Vehicle} is {Telemetry1.MACAddress}")

        print(Telemetry1)
        print(Telemetry2)
        print(Telemetry3)

        break

# End of the example. The rest is for live command sending

def main():
    while True:
        try:
            Data = input()

            Command = ProcessCommand(Data)

            if (Command is not None):
                SendCommand(Command, Vehicle.MRA)

            TelemetryInstance = ReceiveTelemetry(True)

            if (TelemetryInstance is not None):
                print(TelemetryInstance)
        
        except Exception as e:
            print(f"Error: {e}")

def ProcessCommand(Command: str):
    if ((Command.replace(" ", "").upper() == "HEARTBEAT") or (Command.replace(" ", "") == "1")):
        return HeartbeatCommand()
    elif ((Command.replace(" ", "").upper() == "EMERGENCYSTOP") or (Command.replace(" ", "") == "2")):
        return EmergencyStopCommand()
    elif ((Command.replace(" ", "").upper() == "ADDZONE") or (Command.replace(" ", "") == "3")):
        return AddZoneCommand()
    elif ((Command.replace(" ", "").upper() == "PATIENTLOCATION") or (Command.replace(" ", "") == "4")):
        return PatientLocationCommand()
    
    return None

def EmergencyStopCommand():
    print("Emergency Stop Command\nEnter Stop Status:")

    while True:
        Input = input()

        try:
            StopStatus = int(Input)

            return EmergencyStop(StopStatus)
        except ValueError:
            print("Integer Required")

def HeartbeatCommand():
    print("Heartbeat Command\nEnter Connection Status:")

    while True:
        Input = input()

        if ((Input.upper() == "CONNECTED") or (Input == "0")):
            return Heartbeat(ConnectionStatus.Connected)
        elif ((Input.upper() == "UNSTABLE") or (Input == "1")):
            return Heartbeat(ConnectionStatus.Unstable)
        elif ((Input.upper() == "DISCONNECTED") or (Input == "2")):
            return Heartbeat(ConnectionStatus.Disconnected)

def AddZoneCommand():
    print("Add Zone Command\nEnter Zone Type:")

    Coordinates = []
    CoordinateCount = 0
    Zone = None

    while (Zone == None):
        Input = input()

        if ((Input.upper() == "KEEPIN") or (Input == "0")):
            Zone = ZoneType.KeepIn
        elif ((Input.upper() == "KEEPOUT") or (Input == "1")):
            Zone = ZoneType.KeepOut
        elif ((Input.upper() == "SEARCHAREA") or (Input == "2")):
            Zone = ZoneType.SearchArea
    
    print("Enter 3 to 6 Coordinates:")

    while True:
        print(f"Enter Coordinate {CoordinateCount} as (x, y), or q to end:")

        Input = input()

        try:
            if (CoordinateCount < 6):
                if ((Input.upper() == "Q") and (CoordinateCount >= 3)):
                    return AddZone(Zone, Coordinates)

                Coordinate = ast.literal_eval(Input)

                print(Coordinate)

                Coordinates.append(Coordinate)

                CoordinateCount += 1
            else:
                return AddZone(Zone, Coordinates)
        except Exception:
            print("Invalid tuple")

def PatientLocationCommand():
    print("Patient Location Command\nEnter Coordinate as (x, y):")

    while True:
        Input = input()

        try:
            Coordinate = ast.literal_eval(Input)

            return PatientLocation(Coordinate)
        except Exception:
            print("Invalid tuple")

if __name__ == '__main__':
    main()