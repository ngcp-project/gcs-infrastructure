from Command.EmergencyStop import EmergencyStop
from Command.Heartbeat import Heartbeat
from Enum.ConnectionStatus import ConnectionStatus

status = ConnectionStatus.Connected
data1 = Heartbeat(status)
data2 = EmergencyStop(0)

telems = []
telems.append(data1.decode_packet(data1.encode_packet()))
telems.append(data2.decode_packet(data2.encode_packet()))

print(telems)