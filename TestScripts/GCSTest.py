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
Command3 = KeepIn(KeepInCoordinates)

SendCommand(Command1, Vehicle.MRA)
SendCommand(Command2, Vehicle.MRA)
SendCommand(Command3, Vehicle.MRA)

Telemetry1 = ReceiveTelemetry()
Telemetry2 = ReceiveTelemetry()
Telemetry3 = ReceiveTelemetry()

print(f"MAC Address of {Telemetry1.Vehicle} is {Telemetry1.MACAddress}")

print(Telemetry1)
print(Telemetry2)
print(Telemetry3)

# End of the example. The rest is for live command sending

def main():
    while True:
        try:
            Data = input()

            Command = ProcessCommand(Data)

            if (Command is not None):
                SendCommand(Command, Vehicle.MRA)

            Telemetry = ReceiveTelemetry()

            if (Telemetry is not None):
                print(Telemetry)
        
        except Exception as e:
            print(f"Error: {e}")

def ProcessCommand(Command: str):
    if ((Command.replace(" ", "").upper() == "HEARTBEAT") or (Command == "1")):
        return HeartbeatCommand()
    elif ((Command.replace(" ", "").upper() == "EMERGENCYSTOP") or (Command == "2")):
        return EmergencyStopCommand()
    elif ((Command.replace(" ", "").upper() == "KEEPIN") or (Command == "3")):
        return KeepInCommand()
    
    return None

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

def KeepInCommand():
    print("Keep In Command\nEnter up to 6 coordinates:")

    Coordinates = []
    CoordinateCount = 1

    while True:
        print(f"Enter Coordinate {CoordinateCount} as (x, y), or q to end:")

        Input = input()

        try:
            if (CoordinateCount <= 6):
                if (Input.upper() == "Q"):
                    return KeepIn(Coordinates)

                Coordinate = ast.literal_eval(Input)

                print(Coordinate)

                Coordinates.append(Coordinate)

                CoordinateCount += 1
            else:
                return KeepIn(Coordinates)
        except Exception:
            print("Invalid tuple")
        
def EmergencyStopCommand():
    print("Emergency Stop Command\nEnter Stop Status:")

    while True:
        Input = input()

        try:
            StopStatus = int(Input)

            return EmergencyStop(StopStatus)
        except ValueError:
            print("Integer Required")

if __name__ == '__main__':
    main()