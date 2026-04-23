from Command import *
from Enum import *
from Infrastructure.InfrastructureInterface import *
from PacketLibrary.PacketLibrary import PacketLibrary
from Telemetry.Telemetry import Telemetry

import json

PORT = "COM3"

# This is an example script and should be copied and pasted into your repository where you have gcs-infrastructure as a git submodule

# Read gcs-infrastructure documentation to understand the implications of the following function calls

PacketLibrary.SetGCSMACAddress("0013A2004283A0EC")

LaunchVehicleXBee(PORT)

Command1 = ReceiveCommand()
Command2 = ReceiveCommand()
Command3 = ReceiveCommand()

print(Command1)
print(Command2)
print(Command3)

try:
    CommandData1 = json.loads(Command1)
    CommandData2 = json.loads(Command2)
    CommandData3 = json.loads(Command3)
                    
except json.JSONDecodeError as e:
    print(f"JSON Error: {e}")

Telemetry1 = Telemetry(CommandData1["Command ID"], CommandData1["Packet ID"], 100, 0, 0, 0, 45, 0.5, 0, (1, 2), 0, 0, 1.0, 1.0, 0)
Telemetry2 = Telemetry(CommandData2["Command ID"], CommandData2["Packet ID"], 100, 0, 0, 0, 45, 0.5, 0, (1, 2), 0, 0, 1.0, 1.0, 0)
Telemetry3 = Telemetry(CommandData3["Command ID"], CommandData3["Packet ID"], 100, 0, 0, 0, 45, 0.5, 0, (1, 2), 0, 0, 1.0, 1.0, 0)

SendTelemetry(Telemetry1)
SendTelemetry(Telemetry2)
SendTelemetry(Telemetry3)

# End of the example. The rest is for live command receiving

while (True):
    Command = ReceiveCommand()

    print(type(Command))

    try:
        CommandData = json.loads(Command)
        
        match (Command):
            case Heartbeat():
                print("Executing Heartbeat code")
            case EmergencyStop():
                print("Executing Emergency Stop code")
            case KeepIn():
                print("Executing Keep In code")
            case KeepOut():
                print("Executing Keep Out code")
            case PatientLocation():
                print("Executing Patient Location code")
            case SearchArea():
                print("Executing Search Area code")
            case _:
                print("Unknown Command Type")
                    
    except json.JSONDecodeError as e:
        print(f"JSON Error: {e}")

    TelemetryInstance = Telemetry(CommandData["Command ID"], CommandData["Packet ID"], 100, 0, 0, 0, 45, 0.5, 0, (1, 2), 0, 0, 1.0, 1.0, 0)

    SendTelemetry(Telemetry1)