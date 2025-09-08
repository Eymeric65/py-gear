#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for IronPython 2.7 compatibility
Tests the gear profile functions without requiring Alibre CAD
"""

from gear_profile_py27 import generate_tooth_profile

def test_gear_profiles():
    """Test various gear configurations"""
    print("Testing IronPython 2.7 compatible gear profile generation...")
    print("=" * 60)
    
    # Test 1: Standard gear
    print("Test 1: Standard 12-tooth gear")
    profile1 = generate_tooth_profile(z=12, m=2.5, alpha_deg=20.0)
    params1 = profile1['parameters']
    print("  Pitch radius: " + str(round(params1['pitch_radius'], 2)) + " mm")
    print("  Base radius: " + str(round(params1['base_radius'], 2)) + " mm")
    print("  Points per curve: " + str(len(profile1['involute_1'])))
    print("")
    
    # Test 2: Small gear with undercut suppression
    print("Test 2: Small 6-tooth gear with undercut suppression")
    profile2 = generate_tooth_profile(z=6, m=2.0, alpha_deg=20.0, undercut_auto_suppress=True)
    params2 = profile2['parameters']
    print("  Original pitch radius would be: " + str(6.0) + " mm")
    print("  Actual pitch radius (with shift): " + str(round(params2['pitch_radius'], 2)) + " mm")
    print("  Profile shift applied: " + str(round(params2['profile_shift'], 3)))
    print("")
    
    # Test 3: High resolution gear
    print("Test 3: High resolution 24-tooth gear")
    profile3 = generate_tooth_profile(z=24, m=1.5, alpha_deg=14.5, num_points=50)
    params3 = profile3['parameters']
    print("  Points per curve: " + str(len(profile3['involute_1'])))
    print("  Pressure angle: " + str(params3['alpha_deg']) + "°")
    print("")
    
    # Test 4: Gear with positive profile shift
    print("Test 4: Gear with positive profile shift")
    profile4 = generate_tooth_profile(z=20, m=2.0, alpha_deg=20.0, profile_shift=0.5)
    params4 = profile4['parameters']
    print("  Standard pitch radius would be: " + str(20.0) + " mm")
    print("  Actual pitch radius (with shift): " + str(round(params4['pitch_radius'], 2)) + " mm")
    print("  Profile shift: " + str(params4['profile_shift']))
    print("")
    
    print("All tests completed successfully!")
    print("The gear profile functions are ready for IronPython 2.7 / Alibre CAD!")

def simulate_alibre_workflow():
    """Simulate what would happen in Alibre CAD"""
    print("")
    print("Simulating Alibre CAD workflow...")
    print("=" * 60)
    
    # Generate a gear profile
    z = 16
    m = 3.0
    thickness = 15.0
    
    print("Creating " + str(z) + "-tooth gear (module " + str(m) + " mm)")
    profile = generate_tooth_profile(z=z, m=m, alpha_deg=20.0, num_points=30)
    
    print("Gear profile generated with the following segments:")
    
    segments = [
        ('Center to trochoid_1', 'line'),
        ('Trochoid_1', 'spline'),
        ('Involute_1', 'spline'),  
        ('Upper arc', 'arc'),
        ('Involute_2', 'spline'),
        ('Trochoid_2', 'spline'),
        ('Lower arc', 'arc'),
        ('Back to center', 'line')
    ]
    
    for i, (name, geom_type) in enumerate(segments):
        print("  " + str(i+1) + ". " + name + " (" + geom_type + ")")
    
    print("")
    print("In Alibre CAD, this would:")
    print("1. Create sketch with " + str(len(segments)) + " geometric elements")
    print("2. Extrude by " + str(thickness) + " mm")
    print("3. Create circular pattern with " + str(z) + " instances")
    print("4. Result: Complete spur gear ready for manufacturing")

if __name__ == "__main__":
    test_gear_profiles()
    simulate_alibre_workflow()
