# Obstacle Avoidance Drone - DroneKit + YDLidar X2

A complete autonomous obstacle avoidance system for drones using:
- **Pixhawk 2.4.8** autopilot
- **YDLidar X2** 2D LiDAR sensor
- **Raspberry Pi** as onboard computer
- **DroneKit-Python** for drone control

## Hardware Setup

### Components
- Pixhawk 2.4.8 Flight Controller
- YDLidar X2 LiDAR Sensor (360° 2D scanning)
- Raspberry Pi 3B+ or 4B (4GB RAM recommended)
- Telemetry Module (optional for ground monitoring)
- LiPo Battery (3S or 4S)
- Quadcopter frame with motors/ESCs

### Wiring Diagram

#### Pixhawk to Raspberry Pi

**GPIO UART Connection:**
```
Pixhawk UART RX  → Raspberry Pi TX (GPIO 14)
Pixhawk UART TX  → Raspberry Pi RX (GPIO 15)
Pixhawk GND      → Raspberry Pi GND
```

**OR USB Connection (Alternative):**
```
Pixhawk Micro USB → Raspberry Pi USB 2/3
```

#### YDLidar X2 to Raspberry Pi
```
YDLidar USB      → Raspberry Pi USB Port
YDLidar GND      → Pixhawk GND (common ground)
```

### Raspberry Pi Setup

1. **Enable UART for Pixhawk:**
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options → Serial Port
   # Enable serial interface
   ```

2. **Install system dependencies:**
   ```bash
   sudo apt-get update
   sudo apt-get upgrade
   sudo apt-get install python3-pip python3-dev
   sudo apt-get install libopencv-dev python3-opencv
   sudo apt-get install git
   ```

3. **Add user to serial groups:**
   ```bash
   sudo usermod -a -G dialout $USER
   sudo usermod -a -G tty $USER
   # Logout and login for changes to take effect
   ```

4. **Clone project and install:**
   ```bash
   cd /Users/riteshkumar/Desktop/ROBOTICS/Painting\ drone/dronekit_lidar
   pip3 install -r requirements.txt
   ```

## File Structure

```
dronekit_lidar/
├── requirements.txt          # Python dependencies
├── lidar_reader.py          # YDLidar X2 interface
├── drone_controller.py      # DroneKit + Pixhawk control
├── obstacle_avoidance.py    # Avoidance algorithm
├── main.py                  # Main mission script
├── test_lidar.py            # LiDAR diagnostics
├── test_drone.py            # Pixhawk diagnostics
└── README.md                # This file
```

### Module Descriptions

**lidar_reader.py**
- Handles serial communication with YDLidar X2
- Parses distance data from LiDAR
- Provides sector-based distance queries
- Thread-safe data access

**drone_controller.py**
- Interfaces with Pixhawk via DroneKit
- Manages arming, takeoff, landing
- Sends velocity commands
- Retrieves telemetry data

**obstacle_avoidance.py**
- Implements avoidance algorithm
- Monitors 4 directional sectors (Front, Left, Right, Rear)
- Adjusts speed based on obstacle distance
- Three distance thresholds: Critical, Warning, Safe

**main.py**
- Orchestrates complete mission
- Handles setup and pre-flight checks
- Manages autonomous flight
- Safe shutdown and landing

## Quick Start

### Step 1: Test LiDAR
```bash
python3 test_lidar.py
```

**Expected output:**
```
[LiDAR] Initializing YDLidar X2 on port /dev/ttyUSB0...
[LiDAR] Connected to /dev/ttyUSB0 at 128000 baud
Connected, waiting for scan data...

[Scan 1] Received 360 distance points
  Front (0°):  125.5 cm
  Left (90°):   98.3 cm
  Right (270°): 150.2 cm
  Closest: 45.6cm at 15.2°
```

### Step 2: Test Drone Connection
```bash
python3 test_drone.py
```

**Expected output:**
```
[Drone] Initializing connection to /dev/ttyAMA0...
[Drone] Connected to Pixhawk!

=== Drone Status ===
Autopilot: APM:Copter
Battery: 12.80V
Armed: False

Vehicle Information:
  Autopilot: APM:Copter
  Status: STANDBY
  Armed: False

Battery Status:
  Voltage: 12.80V
  Current: 0.50A
  Level: 85%

GPS Status:
  Fix Type: 3
  Satellites: 12
  ✓ GPS locked
```

### Step 3: Run Autonomous Mission
```bash
python3 main.py
```

**Mission sequence:**
1. Connect to LiDAR and Pixhawk
2. Perform pre-flight checks
3. Arm motors
4. Takeoff to 2m altitude
5. Begin obstacle avoidance flight (5 minutes default)
6. Monitor and adjust based on obstacles
7. Land safely
8. Disarm

## Configuration

### Distance Thresholds (obstacle_avoidance.py)

```python
CRITICAL_DISTANCE = 50      # cm - Emergency stop, dodge
WARNING_DISTANCE = 100      # cm - Slow down, start avoidance  
SAFE_DISTANCE = 150         # cm - Resume cruise speed
```

### Speeds (m/s)

```python
CRUISE_SPEED = 0.5          # Normal forward speed
SLOW_SPEED = 0.2            # Obstacle avoidance speed
AVOID_SPEED = 0.3           # Lateral dodge speed
```

### Flight Parameters (main.py)

```python
self.target_altitude = 2.0  # Takeoff altitude in meters
flight_duration = 300       # Autonomous flight time in seconds
```

## Avoidance Algorithm

The system uses a **4-sector directional approach**:

### Sectors
- **Forward (0°)**: Primary flight direction
- **Left (90°)**: Alternative route
- **Right (270°)**: Alternative route
- **Rear (180°)**: Not used (already moving away)

### Decision Logic

```
IF forward_distance < CRITICAL_DISTANCE (50cm):
    → STOP immediately
    → Dodge left if left_distance > right_distance
    → Otherwise dodge right

ELSE IF forward_distance < WARNING_DISTANCE (100cm):
    → SLOW DOWN
    → Steer away from obstacle
    → Maintain forward momentum

ELSE IF forward_distance >= SAFE_DISTANCE (150cm):
    → CRUISE at normal speed

ELSE (between WARNING and SAFE):
    → GRADUAL approach
    → Reduce speed proportionally
    → Continue forward cautiously
```

## Troubleshooting

### LiDAR Issues

**Problem: "Connection failed" on test_lidar.py**
```bash
# Check USB connection
lsusb | grep YD

# Verify port
ls -la /dev/ttyUSB*

# Check permissions
sudo usermod -a -G dialout $USER
```

**Problem: No distance readings**
- Verify LiDAR motor is spinning
- Check USB cable quality
- Try different USB port
- Restart LiDAR: unplug for 10 seconds

**Problem: "Permission denied /dev/ttyUSB0"**
```bash
sudo chmod 666 /dev/ttyUSB0
```

### Pixhawk Issues

**Problem: "Connection failed" on test_drone.py**
```bash
# Verify UART is enabled
sudo raspi-config

# Check serial port
ls -la /dev/ttyAMA0

# Try USB adapter
python3 test_drone.py  # Edit to use /dev/ttyUSB1
```

**Problem: "GPS timeout" during arm**
- Wait 1-2 minutes for GPS lock (first time)
- Check GPS antenna connection
- Ensure clear sky view
- Check LED: should be green = locked

**Problem: "Arm timeout"**
- Check battery voltage (>10.5V for 3S)
- Verify autopilot firmware
- Check gyro calibration
- Ensure drone on level surface

### Altitude Issues

**Problem: Drone drifts down/up**
- Calibrate barometer in Mission Planner
- Ensure takeoff on level surface
- Check GPS signal quality
- Verify weight distribution

**Problem: Takes off but doesn't hover**
- Run compassmot calibration
- Check vibration isolation
- Verify PID gains in firmware

## Safety Checklist

⚠️ **MANDATORY PRE-FLIGHT**
- [ ] Battery fully charged
- [ ] All propellers intact and secure
- [ ] LiDAR motor spinning freely
- [ ] GPS lock obtained (LED green, 3+ satellites)
- [ ] Pixhawk responding to commands
- [ ] Area cleared of obstacles
- [ ] Flying space: minimum 5m × 5m × 3m
- [ ] Safety spotter present
- [ ] No people or animals in flight area
- [ ] Check local drone regulations

## Advanced Customization

### Custom Avoidance Behavior

Edit `obstacle_avoidance.py` `_execute_avoidance()` method:

```python
# Example: Add altitude avoidance
if obstacle_above:
    self.drone.send_velocity_body_frame(0, 0, 0.3)  # Ascend
    self.current_mode = AvoidanceMode.AVOID_UP

# Example: Smart dodge (choose best path)
if forward_dist < WARNING_DISTANCE:
    if left_dist > right_dist + 20:  # 20cm hysteresis
        # Dodge left
    elif right_dist > left_dist + 20:
        # Dodge right
    else:
        # Circle around
```

### Mission Logging

Add to `main.py`:

```python
import csv
from datetime import datetime

def log_flight(self, duration):
    filename = f'flight_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'altitude', 'forward_dist', 'left_dist', 'right_dist', 'mode'])
        
        # In _avoidance_loop:
        writer.writerow([
            datetime.now(),
            self.drone.get_current_altitude(),
            forward_dist,
            left_dist,
            right_dist,
            str(self.current_mode)
        ])
```

### Ground Control Station

Add MAVProxy monitoring:

```bash
mavproxy.py --master=/dev/ttyUSB0 --baudrate=57600 --out=127.0.0.1:14550
```

Then use QGroundControl on another computer on the network.

## Performance Tips

1. **Faster updates**: Reduce `time.sleep()` in `_avoidance_loop` (currently 0.1s = 10Hz)
2. **Smoother avoidance**: Increase `SECTOR_WIDTH` for larger detection cones
3. **Lower latency**: Use USB connection instead of GPIO UART
4. **Better efficiency**: Increase `SAFE_DISTANCE` for preemptive avoidance

## References

- [DroneKit Documentation](http://dronekit.io/api-reference/index.html)
- [Pixhawk Setup Guide](https://ardupilot.org/copter/docs/pixhawk.html)
- [YDLidar X2 Spec Sheet](https://www.ydlidar.com/products/lidar-x2.html)
- [MAVLink Protocol](https://mavlink.io/en/messages/common.html)
- [ArduPilot Copter Docs](https://ardupilot.org/copter/)

## Common Commands

```bash
# Remote access on Raspberry Pi
ssh pi@raspberrypi.local

# Monitor serial port
cat /dev/ttyUSB0

# View system logs
journalctl -u main.py -f

# Kill hanging processes
pkill -f "python3 main.py"

# Update all packages
pip3 install --upgrade -r requirements.txt
```

## License

Educational and research use.

## Support

For issues:
1. Check **Troubleshooting** section
2. Review test script output
3. Check `/tmp/dronekit.log` for errors
4. Consult reference documentation

---

**Last Updated:** March 2026
**Hardware Verified:** Pixhawk 2.4.8, Raspberry Pi 4B, YDLidar X2
# dronekit_lidar
