# GCS Infrastructure

## Submodule

To run ```gcs-infrastructure``` as a submodule:

In the parent directory of the host respository:

1.) ```mkdir lib```

2.) ```cd lib```

3.) ```git submodule add https://github.com/ngcp-project/gcs-infrastructure.git```

4.) ```git submodule add https://github.com/ngcp-project/gcs-packet.git```

5.) ```git submodule add https://github.com/ngcp-project/xbee-python.git```

6.) ```git submodule update --init --recursive```

7.) ```pip install -e "gcs-infrastructure"```

8.) ```pip install -e "gcs-packet"```

9.) ```pip install -e "xbee-python"```

## Standalone

> [!NOTE]
> The only use case to run ```gcs-infrastructure``` like this is internal testing, install it as a submodule to another repository instead for all other use cases

To run ```gcs-infrastructure``` as a standalone repository:

1.) Create and source a venv

2.) Change working directory to  ```gcs-infrastructure/lib```

3.) ```git submodule update --init --recursive```

4.) ```cd ..```

5.) ```pip install -r requirements.txt```

6.) ```pip install -e .```

> [!NOTE]
> If using VS Code, open the command palette and ensure the python interpreter is set to your venv, or ```xbee-python``` and ```gcs-packet``` classes will not be found

To start the GCS XBee:

```python
from InfrastructureInterface import LaunchGCSXBee

LaunchGCSXBee(PORT)
```

To start a vehicle XBee:
```python
from InfrastructureInterface import LaunchVehicleXBee

LaunchVehicleXBee(PORT)
```

> [!NOTE]
> Never call either LaunchXBee function more than once. In the future calling it more than once will return a clearer error. ```LaunchGCSXBee``` and ```LaunchVehicleXBee``` are mutually exclusive and should not be called in the same file

To send a Command:

```python
from InfrastructureInterface import SendCommand

# Assuming LaunchGCSXBee was called earlier, CommandInstance is any Command object

SendCommand(CommandInstance, Vehicle.ALL)
```

To send Telemetry:

```python
from InfrastructureInterface import SendTelemetry

# Assuming LaunchVehicleXbee was called earlier, TelemetryInstance is a Telemetry object

SendTelemetry(TelemetryInstance)
```

To receive a Command:

```python
from InfrastructureInterface import ReceiveCommand

# Assuming LaunchVehicleXBee was called earlier, ReceivedCommand will be assigned to a Command object. Blocking is a boolean that defines whether the queue should block the thread for up to 5 seconds or not. DecodeType is the DecodeFormat the command should be retuned as

ReceivedCommand = ReceiveCommand(Blocking, DecodeType)
```

To receive Telemetry:

```python
from InfrastructureInterface import ReceiveTelemetry

#Assuming LaunchGCSXBee was called earlier, ReceivedTelemetry will be a Telemetry object. Blocking is a boolean that defines whether the queue should block the thread for up to 5 seconds or not.

ReceivedTelemetry = ReceiveTelemetry(Blocking)
```

>[!NOTE]
> ```SendCommand``` and ```ReceiveTelemetry``` will now only block the thread if ```Blocking``` is True. If it is a blocking call the thread will block up to 5 seconds before returning ```None```



## Example Scripts

Test scripts are found in ```gcs-infrastructure/TestScripts```

Run ```GCSTest.py``` in one window and ```VehicleTest.py``` in another to test XBee communication, as well as sending commands and receiving telemetry

### GCSTest.py

Serves as a demo GCS able to send commands and receive telemetry from a vehicle

Commands can be sent either by name or using their Command ID as an alias. Command names are case and whitespace insensitive. Send only the command name or alias, the parameters will be entered seperately

| Command Name | Command ID | Parameters |
| --- | --- | --- |
| Heartbeat | 1 | ConnectionStatus |
| Emergency Stop | 2 | int |
| Keep In | 3 | list<tuple(x, y)>() |
| Keep Out | 4 | list<tuple(x, y)>() |
| Current Patient Location | 5 | tuple(x, y) |
| Search Area | 6 | list<tuple(x, y)>() |

Any other string will be sent as a string literal

### VehicleTest.py

Serves as a demo vehicle able to receive commands, generate telemetry, and send it back to the GCS

## Communication Libraries
<!-- Libraries? Maybe there will be another one made for future iterations of this project :O -->

### XBee Serial Library
This library builds off [pySerial](https://pyserial.readthedocs.io/en/latest/pyserial.html) and allows for the easy transmission and reception of data over the XBee module. This library was made specifically for the [Digi XBee® RR Pro Module][xbee_rr_datasheet].

Refer to the [XBee Serial Library][xbee_readme.md] page for further details and documentation.

## FPV
<!-- TO DO -->

## Additional Libraries
[xbee-python](https://github.com/ngcp-project/xbee-python)

[gcs-packet](https://github.com/ngcp-project/gcs-packet)

## Troubleshooting

Sometimes xbee-python and gcs-packet packages cannot be resolved by Python. If this occurs, it is best to delete the repository and re-clone it. Doing the setup and running the Python scripts in Windows Powershell is recommended. Ensure that the Python interpreter you are using to run the code is using the virtual environment you used to install the libraries.