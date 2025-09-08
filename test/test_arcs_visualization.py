#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple arc visualization test to verify arcs are not full circles
"""

import matplotlib.pyplot as plt
from gear_profile import generate_tooth_profile

# Generate tooth profile
result = generate_tooth_profile(z=5, m=2.0, alpha_deg=20.0, num_points=20)

# Create figure with multiple subplots to isolate each part
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 12))

# Plot upper arc only
if result['upper_arc']:
    x_coords = [p[0] for p in result['upper_arc']]
    y_coords = [p[1] for p in result['upper_arc']]
    ax1.plot(x_coords, y_coords, 'ro-', linewidth=3, markersize=6)
    ax1.set_title('Upper Arc Only')
    ax1.set_aspect('equal')
    ax1.grid(True)
    
    # Add reference circle
    circle = plt.Circle((0, 0), result['parameters']['addendum_radius'], 
                       fill=False, color='gray', linestyle='--', alpha=0.5)
    ax1.add_patch(circle)

# Plot lower arc only  
if result['lower_arc']:
    x_coords = [p[0] for p in result['lower_arc']]
    y_coords = [p[1] for p in result['lower_arc']]
    ax2.plot(x_coords, y_coords, 'bo-', linewidth=3, markersize=6)
    ax2.set_title('Lower Arc Only')
    ax2.set_aspect('equal')
    ax2.grid(True)
    
    # Add reference circle
    circle = plt.Circle((0, 0), result['parameters']['dedendum_radius'], 
                       fill=False, color='gray', linestyle='--', alpha=0.5)
    ax2.add_patch(circle)

# Plot all tooth parts together
parts = ['trochoid_1', 'involute_1', 'upper_arc', 'involute_2', 'trochoid_2', 'lower_arc']
colors = ['purple', 'blue', 'red', 'green', 'magenta', 'orange']

for i, part_name in enumerate(parts):
    part_points = result[part_name]
    if part_points:
        x_coords = [p[0] for p in part_points]
        y_coords = [p[1] for p in part_points]
        ax3.plot(x_coords, y_coords, color=colors[i], linewidth=2, 
                marker='o', markersize=4, label=part_name)

ax3.set_title('All Tooth Parts')
ax3.set_aspect('equal')
ax3.grid(True)
ax3.legend()

# Add reference circles
for radius, color, label in [(result['parameters']['pitch_radius'], 'blue', 'pitch'),
                            (result['parameters']['base_radius'], 'green', 'base'),
                            (result['parameters']['addendum_radius'], 'red', 'addendum'),
                            (result['parameters']['dedendum_radius'], 'orange', 'dedendum')]:
    circle = plt.Circle((0, 0), radius, fill=False, color=color, 
                       linestyle='--', alpha=0.3, label=f'{label} circle')
    ax3.add_patch(circle)

# Plot complete gear (5 teeth)
for tooth_num in range(5):
    tooth_angle = tooth_num * 2 * 3.14159 / 5
    
    for i, part_name in enumerate(parts):
        part_points = result[part_name]
        if part_points:
            # Rotate points
            rotated_points = []
            for x, y in part_points:
                cos_a = abs(tooth_angle)  # Use abs to see rotation effect
                sin_a = abs(tooth_angle)  # Use abs to see rotation effect
                x_rot = x * cos_a - y * sin_a
                y_rot = x * sin_a + y * cos_a
                rotated_points.append((x_rot, y_rot))
            
            x_coords = [p[0] for p in rotated_points]
            y_coords = [p[1] for p in rotated_points]
            
            # Only label first tooth
            label = part_name if tooth_num == 0 else None
            ax4.plot(x_coords, y_coords, color=colors[i], linewidth=2, label=label)

ax4.set_title('Complete Gear (5 teeth)')
ax4.set_aspect('equal')
ax4.grid(True)
ax4.legend()

plt.tight_layout()
plt.show()

# Print arc details
print("Upper arc details:")
for i, (x, y) in enumerate(result['upper_arc']):
    print(f"  Point {i}: ({x:.3f}, {y:.3f})")

print("\nLower arc details:")
for i, (x, y) in enumerate(result['lower_arc']):
    print(f"  Point {i}: ({x:.3f}, {y:.3f})")
