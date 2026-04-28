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

    CommandQueue.put(CommandInstance, False)

    print("Command Queued")

def SendTelemetry(TelemetryInstance: Telemetry):
    TelemetryQueue.put(TelemetryInstance, False)

    print("Telemetry Queued")

def ReceiveCommand(Blocking: bool = False, DecodeResult: DecodeFormat = DecodeFormat.Class) -> CommandInterface | None:
    try:
        Data = CommandQueue.get(Blocking, 5.0)
    except queue.Empty:
        return None

    CommandInstance = None
    
    match(Data.received_data[0]):
        case 1:
            CommandInstance = Heartbeat.DecodePacket(Data.received_data, DecodeResult)

        case 2:
            CommandInstance = EmergencyStop.DecodePacket(Data.received_data, DecodeResult)

        case 3:
            CommandInstance = AddZone.DecodePacket(Data.received_data, DecodeResult)

        case 4:
            CommandInstance = PatientLocation.DecodePacket(Data.received_data, DecodeResult)

        case _:
            print("\nRetrieved data:", Data.received_data.decode("utf-8"))

    CommandQueue.task_done()

    print("Command Received")

    return CommandInstance

def ReceiveTelemetry(Blocking: bool = False) -> Telemetry | None:
    try:
        TelemetryInstance = TelemetryQueue.get(Blocking, 5.0)
    except queue.Empty:
        return None

    TelemetryQueue.task_done()

    print("Telemetry Received")

    return TelemetryInstance