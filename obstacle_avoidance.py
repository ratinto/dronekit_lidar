#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Obstacle Avoidance System
Integrates LiDAR data with DroneKit for autonomous obstacle avoidance
"""

import time
from enum import Enum
from threading import Thread, Lock, Event


class AvoidanceMode(Enum):
    """Avoidance behavior modes"""
    HOVER = 1
    AVOID_LEFT = 2
    AVOID_RIGHT = 3
    AVOID_UP = 4
    AVOID_DOWN = 5
    MOVE_FORWARD = 6


class ObstacleAvoidanceController:
    """Main obstacle avoidance controller"""
    
    def __init__(self, drone_controller, lidar_reader):
        self.drone = drone_controller
        self.lidar = lidar_reader
        
        self.CRITICAL_DISTANCE = 50
        self.WARNING_DISTANCE = 100
        self.SAFE_DISTANCE = 150
        
        self.SECTOR_WIDTH = 45
        
        self.CRUISE_SPEED = 0.5
        self.SLOW_SPEED = 0.2
        self.AVOID_SPEED = 0.3
        
        self.running = False
        self.avoidance_thread = None
        self.lock = Lock()
        self.current_mode = AvoidanceMode.HOVER
        self.stop_event = Event()
        
        print("[Avoidance] Obstacle avoidance controller initialized")
    
    def start(self):
        if self.running:
            print("[Avoidance] Already running")
            return
        
        self.running = True
        self.stop_event.clear()
        self.avoidance_thread = Thread(target=self._avoidance_loop, daemon=True)
        self.avoidance_thread.start()
        print("[Avoidance] Started avoidance system")
    
    def stop(self):
        self.running = False
        self.stop_event.set()
        if self.avoidance_thread:
            self.avoidance_thread.join(timeout=2)
        print("[Avoidance] Stopped avoidance system")
    
    def _avoidance_loop(self):
        while self.running:
            try:
                forward_dist = self.lidar.get_distances_in_sector(0, self.SECTOR_WIDTH)
                left_dist = self.lidar.get_distances_in_sector(90, self.SECTOR_WIDTH)
                right_dist = self.lidar.get_distances_in_sector(270, self.SECTOR_WIDTH)
                
                print(f"[Avoidance] F:{forward_dist} L:{left_dist} R:{right_dist} cm")
                self._execute_avoidance(forward_dist, left_dist, right_dist)
                
                time.sleep(0.1)
            except Exception as e:
                print(f"[Avoidance] Error: {e}")
                time.sleep(0.5)
    
    def _execute_avoidance(self, forward_dist, left_dist, right_dist):
        forward_dist = forward_dist or float('inf')
        left_dist = left_dist or float('inf')
        right_dist = right_dist or float('inf')
        
        if forward_dist < self.CRITICAL_DISTANCE:
            print("[Avoidance] CRITICAL DISTANCE - Emergency stop!")
            self.drone.send_velocity_body_frame(0, 0, 0)
            self.current_mode = AvoidanceMode.HOVER
            
            if left_dist > right_dist:
                print("[Avoidance] Dodging left...")
                self.drone.send_velocity_body_frame(0, self.AVOID_SPEED, 0)
                self.current_mode = AvoidanceMode.AVOID_LEFT
            else:
                print("[Avoidance] Dodging right...")
                self.drone.send_velocity_body_frame(0, -self.AVOID_SPEED, 0)
                self.current_mode = AvoidanceMode.AVOID_RIGHT
        
        elif forward_dist < self.WARNING_DISTANCE:
            print("[Avoidance] WARNING - Obstacle detected")
            
            if left_dist > right_dist:
                print("[Avoidance] Steering left...")
                self.drone.send_velocity_body_frame(self.SLOW_SPEED, self.AVOID_SPEED, 0)
                self.current_mode = AvoidanceMode.AVOID_LEFT
            else:
                print("[Avoidance] Steering right...")
                self.drone.send_velocity_body_frame(self.SLOW_SPEED, -self.AVOID_SPEED, 0)
                self.current_mode = AvoidanceMode.AVOID_RIGHT
        
        elif forward_dist >= self.SAFE_DISTANCE:
            print("[Avoidance] Path clear - Moving forward")
            self.drone.send_velocity_body_frame(self.CRUISE_SPEED, 0, 0)
            self.current_mode = AvoidanceMode.MOVE_FORWARD
        
        else:
            print("[Avoidance] Caution - Cruising")
            reduce_factor = (forward_dist - self.WARNING_DISTANCE) / (self.SAFE_DISTANCE - self.WARNING_DISTANCE)
            forward_speed = self.SLOW_SPEED + (self.CRUISE_SPEED - self.SLOW_SPEED) * reduce_factor
            self.drone.send_velocity_body_frame(forward_speed, 0, 0)
            self.current_mode = AvoidanceMode.MOVE_FORWARD
    
    def set_cruise_speed(self, speed):
        self.CRUISE_SPEED = speed
        print(f"[Avoidance] Cruise speed set to {speed} m/s")
    
    def set_safe_distance(self, distance_cm):
        self.SAFE_DISTANCE = distance_cm
        print(f"[Avoidance] Safe distance set to {distance_cm} cm")
    
    def get_current_mode(self):
        with self.lock:
            return self.current_mode
    
    def hover(self):
        self.drone.send_velocity_body_frame(0, 0, 0)
        self.current_mode = AvoidanceMode.HOVER
        print("[Avoidance] Hovering")
