#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for Pixhawk drone connection
Works on macOS and Linux
"""

import time
import os
from drone_controller import DroneController


def find_pixhawk_port():
    """
    Auto-detect Pixhawk serial port on macOS and Linux
    macOS: /dev/tty.usbmodem* (USB) or /dev/tty.serial* (UART)
    Linux: /dev/ttyACM* (USB) or /dev/ttyAMA0 (GPIO UART)
    """
    import glob
    
    if os.uname().sysname == "Darwin":
        # macOS - Pixhawk via USB
        usb_modem = glob.glob("/dev/tty.usbmodem*")
        if usb_modem:
            return usb_modem[0]
        # Try generic USB serial
        usb_serial = glob.glob("/dev/tty.usb*") + glob.glob("/dev/cu.usb*")
        if usb_serial:
            return usb_serial[0]
        print("[Setup] No USB Pixhawk port found on macOS")
        return None
    else:
        # Linux - Check USB first, then GPIO UART
        acm = glob.glob("/dev/ttyACM*")
        if acm:
            return acm[0]
        if os.path.exists("/dev/ttyAMA0"):
            return "/dev/ttyAMA0"
        return None


def test_drone():
    print("\n" + "="*50)
    print("PIXHAWK DRONE - CONNECTION TEST (macOS/Linux)")
    print("="*50 + "\n")
    
    # Auto-detect port
    drone_port = find_pixhawk_port()
    if not drone_port:
        print("[ERROR] Could not find Pixhawk serial port!")
        print("[Setup] Available USB devices:")
        os.system("ls -la /dev/tty.* 2>/dev/null | grep -E '(usb|modem)' || echo 'No USB devices found'")
        print("\n[Setup] Troubleshooting:")
        print("1. Plug Pixhawk into USB port")
        print("2. Run: ls -la /dev/tty.* | grep usb")
        print("3. Install CH340 driver if needed: https://sparks.gogo.co.nz/ch340.html")
        return False
    
    print(f"[Setup] Auto-detected port: {drone_port}")
    print(f"[Setup] System: {os.uname().sysname}\n")
    
    drone = DroneController(connection_string=drone_port, baud=57600)
    
    if not drone.connect():
        print("[ERROR] Failed to connect to Pixhawk!")
        print("\nTroubleshooting:")
        print("1. Verify USB connection to Pixhawk")
        print("2. Check port: ls -la /dev/tty.usbmodem*")
        print("3. Install USB driver if needed")
        print("4. Restart Pixhawk (unplug/replug USB)")
        print("5. Try different USB cable")
        return False
    
    print("✓ Successfully connected to Pixhawk!\n")
    
    print("Vehicle Information:")
    print(f"  Autopilot: {drone.vehicle.autopilot}")
    print(f"  Status: {drone.vehicle.system_status.state}")
    print(f"  Armed: {drone.vehicle.armed}")
    
    battery = drone.vehicle.battery
    print(f"\nBattery Status:")
    print(f"  Voltage: {battery.voltage:.2f}V")
    print(f"  Current: {battery.current:.2f}A")
    print(f"  Level: {battery.level}%")
    
    if battery.voltage < 10.0:
        print("  ⚠️  WARNING: Low battery voltage!")
    else:
        print("  ✓ Battery OK")
    
    gps = drone.vehicle.gps_0
    print(f"\nGPS Status:")
    print(f"  Fix Type: {gps.fix_type}")
    print(f"  Satellites: {gps.satellites_visible}")
    
    if gps.fix_type < 2:
        print("  ⚠️  WARNING: No GPS lock (expected if indoors)")
    else:
        print("  ✓ GPS locked")
    
    location = drone.vehicle.location
    print(f"\nLocation:")
    print(f"  Global: {location.global_frame}")
    print(f"  Relative: {location.global_relative_frame}")
    
    att = drone.vehicle.attitude
    print(f"\nAttitude:")
    print(f"  Roll:  {att.roll:7.2f}°")
    print(f"  Pitch: {att.pitch:7.2f}°")
    print(f"  Yaw:   {att.yaw:7.2f}°")
    
    drone.disconnect()
    
    print("\n" + "="*50)
    print("✓ Connection test PASSED!")
    print("="*50 + "\n")
    
    return True


if __name__ == "__main__":
    success = test_drone()
    exit(0 if success else 1)
