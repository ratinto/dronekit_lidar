#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DroneKit Controller with Obstacle Avoidance
Controls Pixhawk 2.4.8 autopilot via MAVLink
"""

from dronekit import connect, VehicleMode
import time

class DroneController:
    """Interface for controlling drone via DroneKit"""
    
    def __init__(self, connection_string="/dev/ttyAMA0", baud=57600):
        self.connection_string = connection_string
        self.baud = baud
        self.vehicle = None
        self.is_armed = False
        print(f"[Drone] Initializing connection to {connection_string}...")
    
    def connect(self):
        """Connect to Pixhawk autopilot"""
        try:
            self.vehicle = connect(self.connection_string, baud=self.baud, wait_ready=True, timeout=30)
            print("[Drone] Connected to Pixhawk!")
            self._print_vehicle_info()
            return True
        except Exception as e:
            print(f"[Drone] Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close connection to drone"""
        if self.vehicle:
            self.vehicle.close()
            print("[Drone] Disconnected")
    
    def _print_vehicle_info(self):
        """Print drone status information"""
        print(f"\n=== Drone Status ===")
        print(f"Autopilot: {self.vehicle.autopilot}")
        print(f"Battery: {self.vehicle.battery.voltage}V")
        print(f"Armed: {self.vehicle.armed}\n")
    
    def arm(self):
        """Arm the drone"""
        if self.vehicle is None:
            print("[Drone] Not connected!")
            return False
        
        print("[Drone] Performing pre-flight checks...")
        
        timeout = 0
        while not self.vehicle.gps_0.fix_type > 1:
            print(f"[Drone] Waiting for GPS fix... ({timeout}s)")
            time.sleep(1)
            timeout += 1
            if timeout > 30:
                print("[Drone] GPS timeout!")
                return False
        
        print("[Drone] Arming motors...")
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True
        
        timeout = 0
        while not self.vehicle.armed:
            print("[Drone] Waiting for arm confirmation...")
            time.sleep(1)
            timeout += 1
            if timeout > 10:
                print("[Drone] Arm timeout!")
                return False
        
        self.is_armed = True
        print("[Drone] Armed successfully!")
        return True
    
    def disarm(self):
        """Disarm the drone"""
        if self.vehicle is None:
            return False
        
        self.vehicle.armed = False
        self.is_armed = False
        print("[Drone] Disarmed")
        return True
    
    def takeoff(self, target_altitude):
        """Takeoff to target altitude"""
        if not self.is_armed:
            print("[Drone] Drone must be armed first!")
            return False
        
        print(f"[Drone] Taking off to {target_altitude}m...")
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.simple_takeoff(target_altitude)
        
        while True:
            current_alt = self.vehicle.location.global_relative_frame.alt
            print(f"[Drone] Altitude: {current_alt:.2f}m")
            
            if current_alt >= target_altitude * 0.95:
                print("[Drone] Reached target altitude")
                return True
            
            time.sleep(1)
    
    def land(self):
        """Land the drone"""
        if self.vehicle is None:
            return False
        
        print("[Drone] Landing...")
        self.vehicle.mode = VehicleMode("LAND")
        return True
    
    def send_velocity(self, velocity_x, velocity_y, velocity_z):
        """Send velocity command to drone"""
        if self.vehicle is None:
            return
        
        from pymavlink.dialects.v10 import ardupilotmega as vehicle_types
        msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
            0, 0, 0,
            vehicle_types.MAV_FRAME_BODY_NED,
            0b0000111111000111,
            0, 0, 0,
            velocity_x, velocity_y, velocity_z,
            0, 0, 0,
            0, 0
        )
        self.vehicle.send_mavlink(msg)
    
    def send_velocity_body_frame(self, forward, right, down):
        """Send velocity command in body frame"""
        self.send_velocity(forward, right, -down)
    
    def get_current_altitude(self):
        """Get current altitude"""
        if self.vehicle is None:
            return 0
        return self.vehicle.location.global_relative_frame.alt
    
    def get_attitude(self):
        """Get drone attitude"""
        if self.vehicle is None:
            return 0, 0, 0
        att = self.vehicle.attitude
        return att.roll, att.pitch, att.yaw
    
    def get_location(self):
        """Get drone GPS location"""
        if self.vehicle is None:
            return None
        return self.vehicle.location.global_frame
    
    def is_connected(self):
        """Check if drone is connected"""
        return self.vehicle is not None
