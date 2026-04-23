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

    print("Telemetry Queued")

def ReceiveCommand(DecodeResult: DecodeFormat) -> CommandInterface:
    Data = CommandQueue.get()

    CommandInstance = None
    
    match(Data.received_data[0]):
        case 1:
            CommandInstance = Heartbeat.DecodePacket(Data.received_data, DecodeResult)

        case 2:
            CommandInstance = EmergencyStop.DecodePacket(Data.received_data, DecodeResult)

        case 3:
            CommandInstance = AddZone.DecodePacket(Data.received_data, DecodeResult)

        case 5:
            CommandInstance = PatientLocation.DecodePacket(Data.received_data, DecodeResult)

        case _:
            print("\nRetrieved data:", Data.received_data.decode("utf-8"))

    CommandQueue.task_done()

    print("Command Received")

    return CommandInstance

def ReceiveTelemetry() -> Telemetry:
    TelemetryInstance = TelemetryQueue.get()

    TelemetryQueue.task_done()

    print("Telemetry Received")

    return TelemetryInstance