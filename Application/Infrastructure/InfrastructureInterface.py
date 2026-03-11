from Command import *
from Enum import *
from Infrastructure.GCSXBee import StartXBee
from PacketLibrary.PacketLibrary import PacketLibrary
from Telemetry.Telemetry import Telemetry

from queue import Queue

import ast
import threading

from xbee import XBee

CommandQueue = Queue(maxsize = 0)
TelemetryQueue = Queue(maxsize = 0)

def LaunchXBee(PORT: str):
    StartXBee(PORT, CommandQueue, TelemetryQueue)

def SendCommand(Command: CommandInterface, VehicleName: Vehicle):
    Command.Vehicle = VehicleName

    CommandQueue.put(Command)

    print("Command Queued")

def ReceiveTelemetry():
    TelemetryInstance = TelemetryQueue.get()

    TelemetryQueue.task_done()

    print("Telemetry Received")

    return TelemetryInstance