# GCS Infrastructure

## Standalone

To run ```gcs-infrastructure``` as a standalone repository:

1.) Create and source a venv

2.) Change working directory to  ```gcs-infrastructure/lib```

3.) ```git submodule update --init --recursive```

4.) ```cd ..```

5.) ```pip install -r requirements.txt```

> [!NOTE]
> If using VS Code, open the command palette and ensure the python interpreter is set to your venv, or ```xbee-python``` and ```gcs-packet``` classes will not be found

## Interface

To run ```gcs-infrastructure``` as a submodule:

1.) ```git submodule add https://github.com/ngcp-project/gcs-infrastructure```

2.) ```git submodule update --init --recursive```

3.) ```pip install -e "gcs-infrastructure"```

To start the GCS XBee:

```python
from InfrastructureInterface import LaunchXBee

LaunchXBee(PORT)
```

> [!NOTE]
> Never call LaunchXBee more than once. In the future calling it more than once will return a clearer error

To send a Command

```python
from InfrastructureInterface import SendCommand

#Assuming LaunchXBee was called earlier, Command is any Command object

SendCommand(Command)

```

To receive Telemetry

```python
from InfrastructureInterface import ReceiveTelemetry

#Assuming LaunchXBee was called earlier

TelemetryInstance = ReceiveTelemetry()
```

>[!NOTE]
> ```SendCommand``` and ```ReceiveTelemetry``` are blocking for the duration of time it takes to add to or remove from the queue. This may be made optional later



## Example Scripts

Test scripts are found in ```gcs-infrastructure/TestScripts```

Run CommandTransmitTest.py in one window and TelemetryTransmitTest.py in another to test XBee communication, as well as sending commands and receiving telemetry

### CommandTransmitTest.py

Serves as a demo gcs able to send commands and receive telemetry from a vehicle

Commands can be sent either by name or using their Command ID as an alias. Command names are case and whitespace insensitive. Send only the command name or alias, the parameters will be entered seperately

| Command Name | Command ID | Parameters |
| --- | --- | --- |
| Heartbeat | 1 | ConnectionStatus |
| Emergency Stop | 2 | int |
| Keep In | 3 | tuple(x, y) |

Any other string will be sent as a string literal

### TelemetryTransmitTest.py

Serves as a demo vehicle able to receive commands, generate telemetry, and send it back to the gcs

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

### Logger
Logger builds off of Python's [logging](https://docs.python.org/3/library/logging.html) module and is used to track events that occur when using the XBee serial library (or any other libraries that may be used in the future).

[xbee_readme.md]: ./Communication/XBee/README.md
[xbee_rr_datasheet]: ./Communication/XBee/docs/files/digi-xbee-rr-802-15-4-rf-module-datasheet.pdf

## Troubleshooting

Sometimes xbee-python and gcs-packet packages cannot be resolved by Python. If this occurs, it is best to delete the repository and re-clone it. Doing the setup and running the Python scripts in Windows Powershell is recommended. Ensure that the Python interpreter you are using to run the code is using the virtual environment you used to install the libraries.