# Run Commands (ROS and Non-ROS)

## 1) One-time setup for gcs-infrastructure (non-ROS)
Run from repository root.

```bash
cd /Users/aro/Documents/gcs-infrastructure
python3 -m venv .venv
source .venv/bin/activate
git submodule update --init --recursive
pip install -r requirements.txt
```

Optional: make Application package imports easy in shell sessions.

```bash
export PYTHONPATH="$PWD/Application:$PYTHONPATH"
```

## 2) Start GCS telemetry receiver (infrastructure path)
Open Terminal A.

```bash
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
```

## 3) Non-ROS telemetry sender test (quick sanity check)
Open Terminal B. This validates GCS receive independent of ROS.

```bash
cd /Users/aro/Documents/gcs-infrastructure
source .venv/bin/activate
python3 Demo/vehicle.py
```

Note:
- Demo/vehicle.py contains hard-coded serial port and MAC values.
- Edit those values first to match your hardware.

## 4) Build ROS workspace for XSens bridge
If XSens is your catkin workspace root:

```bash
cd /Users/aro/Documents/gcs-infrastructure/XSens
source /opt/ros/noetic/setup.bash
catkin_make
source devel/setup.bash
```

If needed, build xspublic manually once:

```bash
cd /Users/aro/Documents/gcs-infrastructure/XSens
pushd src/xsens_ros_mti_driver/lib/xspublic
make
popd
```

## 5) Run XSens -> GCS bridge
Open Terminal C.

```bash
cd /Users/aro/Documents/gcs-infrastructure/XSens
source /opt/ros/noetic/setup.bash
source devel/setup.bash
roslaunch xsens_mti_driver xsens_mti_with_gcs_bridge.launch xbee_port:=/dev/ttyUSB0 send_rate_hz:=1.0
```

## 6) Optional ROS health checks
From any ROS-sourced terminal:

```bash
rostopic list | grep filter
rostopic echo /filter/positionlla
rostopic hz /filter/velocity
```

## 7) Optional direct bridge run without launch file
Use rosrun and pass private params with leading underscore.

```bash
cd /Users/aro/Documents/gcs-infrastructure/XSens
source /opt/ros/noetic/setup.bash
source devel/setup.bash
rosrun xsens_mti_driver xsens_to_gcs_bridge.py _xbee_port:=/dev/ttyUSB0 _send_rate_hz:=1.0
```

## 8) Typical full integration startup order
1. Terminal A: start GCS receiver.
2. Terminal C: launch XSens bridge.
3. Watch telemetry print on Terminal A.

## 9) Stop commands
Use Ctrl+C in each terminal.
