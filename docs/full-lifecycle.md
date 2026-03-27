What to run (ROS graph vs bridge)
You don’t manually start “subscribers” in the bridge first. xsens_to_gcs_bridge.py only works after ROS is running and the xsens_mti_node publishers exist.

Best workflow: use the provided launch file, which starts both:

the XSens ROS driver (xsens_mti_node)
the bridge (xsens_to_gcs_bridge.py)
That launch file is XSens/src/xsens_ros_mti_driver/launch/xsens_mti_with_gcs_bridge.launch.

Full lifecycle (commands)
1) One-time setup (Python + submodules)
Run from repo root:

cd /Users/aro/Documents/gcs-infrastructure
python3 -m venv .venv
source .venv/bin/activate
git submodule update --init --recursive
pip install -r requirements.txt
2) Start the GCS receiver (non-ROS; Terminal A)
Run on the GCS machine (the one connected to the GCS XBee serial port):

cd /Users/aro/Documents/gcs-infrastructure
source .venv/bin/activate
export PYTHONPATH="$PWD/Application:$PYTHONPATH"
python3 - <<'PY'
from Infrastructure.InfrastructureInterface import LaunchGCSXBee, ReceiveTelemetry
PORT = "/dev/tty.usbserial-REPLACE_GCS_XBEE_PORT"
LaunchGCSXBee(PORT)
print("GCS receiver started on", PORT)
while True:
    telemetry = ReceiveTelemetry()
    print(telemetry)
PY
Notes:

Replace PORT with your GCS XBee serial device.
You should see telemetry print here once the vehicle sends.
3) Build the ROS workspace for XSens (Vehicle side)
On the vehicle machine:

cd /Users/aro/Documents/gcs-infrastructure/XSens
source /opt/ros/noetic/setup.bash   # change noetic if you use a different ROS1 distro
catkin_make
source devel/setup.bash
(If you already built this recently, you may skip it.)

4) Start XSens + the bridge (Terminal C) recommendeds
On the vehicle machine:

cd /Users/aro/Documents/gcs-infrastructure/XSens
source /opt/ros/noetic/setup.bash
source devel/setup.bash
roslaunch xsens_mti_driver xsens_mti_with_gcs_bridge.launch \
  xbee_port:=/dev/ttyUSB0 \
  send_rate_hz:=1.0 \
  battery_life_default:=1.0 \
  patient_status_default:=0 \
  message_flag_default:=0 \
  message_lat_default:=0.0 \
  message_lon_default:=0.0
This automatically:

starts xsens_mti_node (publishes topics like filter/positionlla, filter/euler, etc.)
starts xsens_to_gcs_bridge.py (subscribes to those topics and sends telemetry over XBee)
Optional: start them separately
If you want to start the XSens node first:

4a) Terminal: XSens driver only
cd /Users/aro/Documents/gcs-infrastructure/XSens
source /opt/ros/noetic/setup.bash
source devel/setup.bash
roslaunch xsens_mti_driver xsens_mti_node.launch
4b) Terminal: bridge only (subscribers + sending)
cd /Users/aro/Documents/gcs-infrastructure/XSens
source /opt/ros/noetic/setup.bash
source devel/setup.bash
rosrun xsens_mti_driver xsens_to_gcs_bridge.py _xbee_port:=/dev/ttyUSB0 _send_rate_hz:=1.0
5) Verify it’s working
On any ROS-sourced terminal (vehicle side):

rostopic list | grep filter
rostopic echo /filter/positionlla
rostopic hz /filter/velocity
On the GCS terminal you should see telemetry objects being printed.

Important caveat (to actually transmit)
The vehicle bridge sends to PacketLibrary.GetGCSMACAddress(), and that value defaults to empty unless you set it somewhere else. So to make the radio transmission work, ensure lib/gcs-packet/Packet/PacketLibrary/PacketLibrary.py has GCS_MAC_ADDRESS set to your GCS XBee 64-bit address (16 hex chars).

If you tell me your GCS XBee MAC, I can patch the bridge to accept a ROS param (so you don’t have to edit library code), and I’ll update the xsens-to-gcs-code-explained.md accordingly.