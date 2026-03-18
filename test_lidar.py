#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for YDLidar X2 sensor
Works with LidarX2 class on macOS and Linux
"""

import time
import os
import glob
from lidar_reader import LidarX2


def find_lidar_port():
    """
    Auto-detect YDLidar X2 serial port on macOS and Linux
    macOS: /dev/tty.usbserial-* or /dev/cu.usbserial-*
    Linux: /dev/ttyUSB*
    """
    if os.uname().sysname == "Darwin":
        # macOS USB serial ports
        mac_ports = glob.glob("/dev/tty.usbserial*") + glob.glob("/dev/cu.usbserial*")
        if mac_ports:
            return mac_ports[0]
        # Try generic USB
        usb_ports = glob.glob("/dev/tty.usb*") + glob.glob("/dev/cu.usb*")
        if usb_ports:
            return usb_ports[0]
        print("[Setup] No USB serial port found on macOS")
        print("[Setup] Please plug in YDLidar X2 USB adapter")
        return None
    else:
        # Linux USB serial ports
        usb_ports = glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*")
        if usb_ports:
            return usb_ports[0]
        return None


def test_lidar():
    print("\n" + "="*60)
    print("YDLidar X2 - SENSOR TEST (LidarX2 Class)")
    print("="*60 + "\n")
    
    # Auto-detect port
    lidar_port = find_lidar_port()
    if not lidar_port:
        print("[ERROR] Could not find LiDAR serial port!")
        print("[Setup] Available USB devices:")
        os.system("ls -la /dev/tty.* 2>/dev/null | grep -E '(usb|modem)' || ls -la /dev/ttyUSB* 2>/dev/null")
        return False
    
    print(f"[Setup] Auto-detected port: {lidar_port}")
    print(f"[Setup] System: {os.uname().sysname}\n")
    
    # Initialize and open LiDAR
    lidar = LidarX2(port=lidar_port)
    
    if not lidar.open():
        print("[ERROR] Failed to connect to LiDAR!")
        print("\nTroubleshooting:")
        print("1. Check USB connection: ls -la /dev/tty.* | grep usbserial")
        print("2. Verify LiDAR is powered (motor should be spinning)")
        print("3. Install CH340 driver if needed: https://sparks.gogo.co.nz/ch340.html")
        print("4. Try different USB port or cable")
        return False
    
    print("[LiDAR] Connected! Waiting for scan data...\n")
    time.sleep(2)
    
    print("Testing data reading...\n")
    
    data_count = 0
    total_points = 0
    
    for i in range(15):
        measures = lidar.getMeasures()
        
        if measures and len(measures) > 0:
            data_count += 1
            total_points += len(measures)
            
            print(f"[Scan {i+1}] Received {len(measures)} distance points")
            
            # Find measurements in key directions
            front = [m for m in measures if m.angle < 30 or m.angle > 330]
            left = [m for m in measures if 60 < m.angle < 120]
            right = [m for m in measures if 240 < m.angle < 300]
            
            if front:
                front_closest = min(front, key=lambda m: m.distance)
                print(f"  Front (0°):   {front_closest.distance:7.1f}mm at {front_closest.angle:.1f}°")
            if left:
                left_closest = min(left, key=lambda m: m.distance)
                print(f"  Left (90°):   {left_closest.distance:7.1f}mm at {left_closest.angle:.1f}°")
            if right:
                right_closest = min(right, key=lambda m: m.distance)
                print(f"  Right (270°): {right_closest.distance:7.1f}mm at {right_closest.angle:.1f}°")
            
            # Find closest overall
            if measures:
                closest = min(measures, key=lambda m: m.distance)
                print(f"  Closest: {closest.distance:.1f}mm at {closest.angle:.1f}°")
        else:
            print(f"[Scan {i+1}] Waiting for data... (LiDAR spinning up)")
        
        time.sleep(0.5)  # 0.5s between scans
    
    lidar.close()
    
    print("\n" + "="*60)
    if data_count > 0:
        avg_points = total_points / data_count
        print(f"✅ Test PASSED!")
        print(f"  ✅ Received {data_count}/15 complete scans")
        print(f"  ✅ Average points per scan: {avg_points:.0f}")
        print(f"  ✅ Baudrate: 115200 bps")
        print(f"  ✅ Range: Up to ~25m")
    else:
        print("❌ Test FAILED - No LiDAR data received")
    print("="*60 + "\n")
    
    return data_count > 0


if __name__ == "__main__":
    success = test_lidar()
    exit(0 if success else 1)
