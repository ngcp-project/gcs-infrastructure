from Command import *
from Enum.ConnectionStatus import ConnectionStatus
from GCSXBee import *
from Telemetry.Telemetry import Telemetry

from queue import Queue

import ast
import threading

from xbee import XBee

#PORT = "COM4"
BAUD_RATE = 115200
DESTINATION = "0013A200428396C0"

CommandQueue = Queue(maxsize = 0)
TelemetryQueue = Queue(maxsize = 0)

def SendCommand(Command: CommandInterface):
    pass