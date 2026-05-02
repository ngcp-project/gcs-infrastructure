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

Command1 = None
Command2 = None
Command3 = None

while True:
    if (Command1 is None):
        Command1 = ReceiveCommand(False, DecodeFormat.Class)

        continue

    if (Command2 is None):
        Command2 = ReceiveCommand(False, DecodeFormat.JSON)

        continue

    if (Command3 is None):
        Command3 = ReceiveCommand(False, DecodeFormat.Class)

        continue

    if ((Command1 != None) and (Command2 != None) and (Command3 != None)):
        print(Command1)
        print(Command2)
        print(Command3)

        break
try:
    CommandData2 = json.loads(Command2)

except json.JSONDecodeError as e:
    print(f"JSON Error: {e}")

Telemetry1 = Telemetry(Command1.COMMAND_ID, Command1.PacketID, 100, 0, 0, 0, 45, 0.5, 0, (1, 2), 0, 0, 1.0, 1.0, 0)
Telemetry2 = Telemetry(CommandData2["Command ID"], CommandData2["Packet ID"], 100, 0, 0, 0, 45, 0.5, 0, (1, 2), 0, 0, 1.0, 1.0, 0)
Telemetry3 = Telemetry(Command3.COMMAND_ID, Command3.PacketID, 100, 0, 0, 0, 45, 0.5, 0, (1, 2), 0, 0, 1.0, 1.0, 0)

SendTelemetry(Telemetry1)
SendTelemetry(Telemetry2)
SendTelemetry(Telemetry3)

# End of the example. The rest is for live command receiving

while (True):
    Command = ReceiveCommand(False, DecodeFormat.Class)

    if (Command is None):
        continue

    print(Command)

    try:
        if (isinstance(Command, str)):
            CommandData = json.loads(Command)
        
        match (Command):
            case Heartbeat():
                print("Executing Heartbeat code")
            case EmergencyStop():
                print("Executing Emergency Stop code")
            case AddZone():
                print("Executing Add Zone code")
            case PatientLocation():
                print("Executing Patient Location code")
            case _:
                print("Unknown Command Type")
                    
    except json.JSONDecodeError as e:
        print(f"JSON Error: {e}")

    print(f"{Command.COMMAND_ID} {Command.PacketID} {Command.PACKET_ID}")
    
    if (isinstance(Command, str)):
        TelemetryInstance = Telemetry(CommandData["Command ID"], CommandData["Packet ID"], 100, 0, 0, 0, 45, 0.5, 0, (1, 2), 0, 0, 1.0, 1.0, 0)
    else:
        TelemetryInstance = Telemetry(Command.COMMAND_ID, Command.PacketID, 100, 0, 0, 0, 45, 0.5, 0, (1, 2), 0, 0, 1.0, 1.0, 0)

    SendTelemetry(TelemetryInstance)