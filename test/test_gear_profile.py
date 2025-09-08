#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test of the gear_profile function - demonstrates usage without matplotlib.
This shows how the function can be used in CAD software with only the math library.
"""

from gear_profile import generate_tooth_profile

def print_profile_summary(profile_data):
    """Print a summary of the generated profile data"""
    params = profile_data['parameters']
    
    print(f"Gear Parameters:")
    print(f"  Teeth: {params['z']}")
    print(f"  Module: {params['m']} mm")
    print(f"  Pressure angle: {params['alpha_deg']}°")
    print(f"  Profile shift: {params['profile_shift']}")
    print(f"  Pitch radius: {params['pitch_radius']:.3f} mm")
    print(f"  Base radius: {params['base_radius']:.3f} mm")
    print(f"  Addendum radius: {params['addendum_radius']:.3f} mm")
    print(f"  Dedendum radius: {params['dedendum_radius']:.3f} mm")
    print()
    
    # Print point counts for each profile part
    parts = ['trochoid_1', 'involute_1', 'upper_arc', 'involute_2', 'trochoid_2', 'lower_arc']
    for part in parts:
        points = profile_data[part]
        if points:
            print(f"{part}: {len(points)} points")
            print(f"  First point: ({points[0][0]:.3f}, {points[0][1]:.3f})")
            print(f"  Last point: ({points[-1][0]:.3f}, {points[-1][1]:.3f})")
        else:
            print(f"{part}: No points (empty)")
        print()

if __name__ == "__main__":
    # Test different gear configurations
    
    print("=== Test 1: Standard gear ===")
    profile1 = generate_tooth_profile(z=12, m=2.5, alpha_deg=20.0, num_points=10)
    print_profile_summary(profile1)
    
    print("=== Test 2: Gear with positive profile shift ===")
    profile2 = generate_tooth_profile(z=8, m=3.0, alpha_deg=25.0, profile_shift=0.5, num_points=10)
    print_profile_summary(profile2)
    
    print("=== Test 3: Small gear with undercut suppression ===")
    profile3 = generate_tooth_profile(z=6, m=2.0, alpha_deg=20.0, undercut_auto_suppress=True, num_points=10)
    print_profile_summary(profile3)
    
    print("=== Test 4: High resolution profile ===")
    profile4 = generate_tooth_profile(z=20, m=1.5, alpha_deg=14.5, num_points=50)
    print(f"High resolution gear with {len(profile4['involute_1'])} points per involute curve")
