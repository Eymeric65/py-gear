#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to check arc angle ranges
"""

import math
from gear_profile import generate_tooth_profile

def debug_arc_angles():
    """Debug the arc angle calculations"""
    # Same parameters as involute.py
    z = 5
    m = 2.0
    alpha_deg = 20.0
    profile_shift = 0.0
    
    # Calculate the same way as original
    alpha = math.radians(alpha_deg)
    rp = m * z / 2.0
    rb = rp * math.cos(alpha)
    rp += profile_shift
    ra = rp + m
    rd = max(rp - 1.25*m, 0.01)
    
    offset_angle = math.acos(rb/rp)
    
    def involute(alpha):
        return math.tan(alpha) - alpha
    
    phi = involute(offset_angle)
    angular_width = math.pi/z
    tooth_angle = -angular_width - 2*phi
    
    # Upper arc angles
    addendum_angle = math.acos(rb/ra)
    involute_at_addendum = involute(addendum_angle)
    
    upper_start = -involute_at_addendum
    upper_end = tooth_angle + involute_at_addendum
    
    print(f"Upper arc angles:")
    print(f"  Start: {upper_start:.6f} rad ({math.degrees(upper_start):.2f}°)")
    print(f"  End: {upper_end:.6f} rad ({math.degrees(upper_end):.2f}°)")
    print(f"  Range: {upper_end - upper_start:.6f} rad ({math.degrees(upper_end - upper_start):.2f}°)")
    
    # Check if this spans more than 180 degrees (pi radians)
    if abs(upper_end - upper_start) > math.pi:
        print("  WARNING: Upper arc spans more than 180°!")
    
    # Lower arc angles (if applicable)
    if rb > rd:
        # Need to calculate beta_trochoid
        t_trochoid = rb - rd
        b_trochoid = math.sqrt(rb**4/(rb-t_trochoid)**2 - rb**2)
        h_trochoid = b_trochoid*(1-t_trochoid/rb)
        alpha_trochoid = math.atan(h_trochoid/rb)
        offset_trochoid_angle = alpha_trochoid + involute(alpha_trochoid)
        beta_trochoid = math.atan(b_trochoid/rb) - offset_trochoid_angle
        
        lower_start = tooth_angle - beta_trochoid
        lower_end = -angular_width*2 + beta_trochoid
        
        print(f"\nLower arc angles:")
        print(f"  Start: {lower_start:.6f} rad ({math.degrees(lower_start):.2f}°)")
        print(f"  End: {lower_end:.6f} rad ({math.degrees(lower_end):.2f}°)")
        print(f"  Range: {lower_end - lower_start:.6f} rad ({math.degrees(lower_end - lower_start):.2f}°)")
        
        # Check if this spans more than 180 degrees (pi radians)
        if abs(lower_end - lower_start) > math.pi:
            print("  WARNING: Lower arc spans more than 180°!")

if __name__ == "__main__":
    debug_arc_angles()
    
    # Test the function
    print("\n" + "="*50)
    print("Testing gear_profile function...")
    result = generate_tooth_profile(z=5, m=2.0, alpha_deg=20.0, num_points=5)
    
    print(f"Upper arc points: {len(result['upper_arc'])}")
    for i, (x, y) in enumerate(result['upper_arc']):
        angle = math.atan2(y, x)
        radius = math.sqrt(x*x + y*y)
        print(f"  Point {i}: ({x:.3f}, {y:.3f}) - angle: {angle:.3f} rad ({math.degrees(angle):.1f}°), radius: {radius:.3f}")
    
    print(f"\nLower arc points: {len(result['lower_arc'])}")
    for i, (x, y) in enumerate(result['lower_arc']):
        angle = math.atan2(y, x)
        radius = math.sqrt(x*x + y*y)
        print(f"  Point {i}: ({x:.3f}, {y:.3f}) - angle: {angle:.3f} rad ({math.degrees(angle):.1f}°), radius: {radius:.3f}")
