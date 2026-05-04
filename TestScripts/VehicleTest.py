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

while (True):
    Command = ReceiveCommand(False, DecodeFormat.Class)

    if (Command is not None):

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
    
        if (isinstance(Command, str)):
            TelemetryInstance = Telemetry(CommandData["Command ID"], CommandData["Packet ID"], 100, 0, 0, 0, 45, 0.5, 0, (1, 2), 0, 0, 1.0, 1.0, 0)
        else:
            TelemetryInstance = Telemetry(Command.COMMAND_ID, Command.PacketID, 100, 0, 0, 0, 45, 0.5, 0, (1, 2), 0, 0, 1.0, 1.0, 0)

        SendTelemetry(TelemetryInstance)