* Check data length of string to be transmitted
* `__transmitting` and `__receiving` fields are not used. May be unnecessary because the thread blocks, meaning only one method can be executed at the same time
* Verify if a Tx is successful or not if possible. XTCU is able to determine whether or not a Tx is successful.
* It may possible for a data frame to be missing bytes when received
* Retrieve data should probably start receiving a new data frame when the start delimeter is read.
* XBee modules seem to always receive data.
* XBee modules must be supplied with enough voltage
    * https://cdn.sparkfun.com/assets/3/c/c/7/e/digi-xbee-rr-802-15-4-rf-module-datasheet.pdf
    * Power Requirements:
        * Supply Voltage: 1.71 - 3.8 V
        * Transmit Current: 193 mA at 3.3 V, +19 dBm
        * Receive Current: 14 mA
        * Sleep Current: 8 µA at 25 ºC (77 ºF) (RF modules will most likely never be sleeping)

__retrieve_status()
* Might read telemetry data instead of the status
