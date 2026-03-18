#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main Mission Script - Obstacle Avoidance Drone
Integrates DroneKit + YDLidar X2 + Pixhawk 2.4.8
"""

import sys
import time
import signal
from drone_controller import DroneController
from lidar_reader import YDLidarX2
from obstacle_avoidance import ObstacleAvoidanceController


class ObstacleAvoidanceMission:
    """Main mission controller"""
    
    def __init__(self):
        self.drone = DroneController(connection_string="/dev/ttyAMA0", baud=57600)
        self.lidar = YDLidarX2(port="/dev/ttyUSB0", baudrate=128000)
        self.avoidance = None
        self.target_altitude = 2.0
        self.mission_running = False
    
    def setup(self):
        print("\n" + "="*50)
        print("OBSTACLE AVOIDANCE DRONE - SETUP")
        print("="*50 + "\n")
        
        print("[Setup] Connecting to LiDAR...")
        if not self.lidar.connect():
            print("[Setup] FAILED: LiDAR connection failed")
            return False
        
        time.sleep(2)
        
        print("[Setup] Connecting to Drone...")
        if not self.drone.connect():
            print("[Setup] FAILED: Drone connection failed")
            self.lidar.disconnect()
            return False
        
        self.avoidance = ObstacleAvoidanceController(self.drone, self.lidar)
        print("[Setup] All systems ready!")
        return True
    
    def pre_flight_checks(self):
        print("\n" + "-"*50)
        print("PRE-FLIGHT CHECKS")
        print("-"*50 + "\n")
        
        if not self.lidar.is_connected():
            print("[Check] FAILED: LiDAR not connected")
            return False
        print("[Check] ✓ LiDAR connected")
        
        if not self.drone.is_connected():
            print("[Check] FAILED: Drone not connected")
            return False
        print("[Check] ✓ Drone connected")
        
        battery = self.drone.vehicle.battery
        print(f"[Check] ✓ Battery: {battery.voltage:.2f}V")
        
        print("\n[Check] All pre-flight checks passed!")
        return True
    
    def arm_and_takeoff(self):
        print("\n" + "-"*50)
        print("ARM AND TAKEOFF")
        print("-"*50 + "\n")
        
        if not self.drone.arm():
            print("[Takeoff] FAILED: Could not arm drone")
            return False
        
        time.sleep(1)
        
        if not self.drone.takeoff(self.target_altitude):
            print("[Takeoff] FAILED")
            self.drone.disarm()
            return False
        
        print("[Takeoff] Ready for autonomous flight")
        return True
    
    def autonomous_flight(self, duration=60):
        print("\n" + "-"*50)
        print("AUTONOMOUS OBSTACLE AVOIDANCE")
        print("-"*50 + "\n")
        
        self.avoidance.start()
        self.mission_running = True
        start_time = time.time()
        
        try:
            print(f"[Mission] Flying for {duration} seconds...")
            while self.mission_running and time.time() - start_time < duration:
                alt = self.drone.get_current_altitude()
                
                if alt < self.target_altitude - 0.5:
                    print("[Mission] Altitude low, ascending...")
                    self.drone.send_velocity_body_frame(0, 0, -0.2)
                
                time.sleep(0.5)
            
            print("[Mission] Flight time complete")
        except KeyboardInterrupt:
            print("\n[Mission] Flight interrupted")
        finally:
            self.avoidance.stop()
            self.mission_running = False
    
    def landing(self):
        print("\n" + "-"*50)
        print("LANDING")
        print("-"*50 + "\n")
        
        if self.avoidance and self.avoidance.running:
            self.avoidance.stop()
        
        self.drone.land()
        
        while self.drone.vehicle.armed:
            alt = self.drone.get_current_altitude()
            print(f"[Landing] Altitude: {alt:.2f}m")
            time.sleep(1)
        
        print("[Landing] Landed safely")
    
    def cleanup(self):
        print("\n" + "-"*50)
        print("CLEANUP")
        print("-"*50 + "\n")
        
        if self.avoidance:
            self.avoidance.stop()
        
        if self.drone.is_armed:
            self.drone.disarm()
        
        self.drone.disconnect()
        self.lidar.disconnect()
        print("[Cleanup] All systems shutdown")
    
    def run(self, flight_duration=60):
        try:
            if not self.setup():
                return False
            
            if not self.pre_flight_checks():
                self.cleanup()
                return False
            
            print("\n" + "="*50)
            print("Ready for obstacle avoidance flight!")
            print("="*50)
            print("\nPress ENTER to continue, or Ctrl+C to abort...")
            try:
                input()
            except KeyboardInterrupt:
                print("\nAborted")
                self.cleanup()
                return False
            
            if not self.arm_and_takeoff():
                self.cleanup()
                return False
            
            self.autonomous_flight(flight_duration)
            self.landing()
            self.cleanup()
            
            print("\n" + "="*50)
            print("MISSION COMPLETE")
            print("="*50 + "\n")
            return True
            
        except Exception as e:
            print(f"\nFATAL ERROR: {e}")
            self.cleanup()
            return False


def main():
    def signal_handler(sig, frame):
        print("\n\nShutting down...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    mission = ObstacleAvoidanceMission()
    success = mission.run(flight_duration=300)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
