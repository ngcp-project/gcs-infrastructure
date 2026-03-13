from Command import *
from Enum import *
from Infrastructure.GCSXBee import StartGCSXBee
from Infrastructure.VehicleXBee import StartVehicleXBee
from Infrastructure.PacketQueue import *
from Telemetry.Telemetry import Telemetry

def LaunchGCSXBee(PORT: str):
    StartGCSXBee(PORT)

def LaunchVehicleXBee(PORT: str):
    StartVehicleXBee(PORT)

def SendCommand(CommandInstance: CommandInterface, VehicleName: Vehicle):
    CommandInstance.Vehicle = VehicleName

    CommandQueue.put(CommandInstance)

    print("Command Queued")

def SendTelemetry(TelemetryInstance: Telemetry):
    TelemetryQueue.put(TelemetryInstance)

    print("Command Queued")

def ReceiveCommand() -> CommandInterface:
    CommandInstance = CommandQueue.get()

    CommandQueue.task_done()

    print("Command Received")

    return CommandInstance

def ReceiveTelemetry() -> Telemetry:
    TelemetryInstance = TelemetryQueue.get()

    TelemetryQueue.task_done()

    print("Telemetry Received")

    return TelemetryInstance