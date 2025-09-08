# Gear Profile Generator - CAD Integration Guide

## Overview

The `gear_profile.py` script provides a pure Python function `generate_tooth_profile()` that generates precise spur gear tooth profiles using only the standard `math` library. This makes it perfect for integration into CAD software.

## Function Signature

```python
def generate_tooth_profile(z, m, alpha_deg, profile_shift=0.0, undercut_auto_suppress=False, num_points=20):
```

## Parameters

- **z** (int): Number of teeth
- **m** (float): Module in mm 
- **alpha_deg** (float): Pressure angle in degrees (typically 14.5° or 20°)
- **profile_shift** (float): Profile shifting coefficient (default: 0.0)
- **undercut_auto_suppress** (bool): Automatically calculate profile shift to prevent undercut (default: False)
- **num_points** (int): Number of points per curve segment (default: 20)

## Return Value

Returns a dictionary with 6 tooth profile parts and parameters:

```python
{
    'trochoid_1': [(x1, y1), (x2, y2), ...],    # First trochoid curve
    'involute_1': [(x1, y1), (x2, y2), ...],    # First involute curve  
    'upper_arc': [(x1, y1), (x2, y2), ...],     # Upper addendum arc
    'involute_2': [(x1, y1), (x2, y2), ...],    # Second involute curve
    'trochoid_2': [(x1, y1), (x2, y2), ...],    # Second trochoid curve
    'lower_arc': [(x1, y1), (x2, y2), ...],     # Lower dedendum arc
    'parameters': {
        'z': z,
        'm': m,
        'alpha_deg': alpha_deg,
        'profile_shift': profile_shift,
        'pitch_radius': pitch_radius,
        'base_radius': base_radius,
        'addendum_radius': addendum_radius,
        'dedendum_radius': dedendum_radius
    }
}
```

## Tooth Profile Order

One complete tooth consists of these 6 parts connected in sequence:
1. **trochoid_1** → **involute_1** → **upper_arc** → **involute_2** → **trochoid_2** → **lower_arc**

## CAD Integration Example

```python
import math
from gear_profile import generate_tooth_profile

# Generate gear tooth profile
profile = generate_tooth_profile(z=20, m=2.5, alpha_deg=20.0, num_points=30)

# Create complete gear by rotating tooth around z-axis
def create_full_gear(tooth_profile, z):
    full_gear_points = []
    
    for tooth_num in range(z):
        rotation_angle = tooth_num * 2 * math.pi / z
        
        # Rotate each part of the tooth profile
        for part_name in ['trochoid_1', 'involute_1', 'upper_arc', 
                         'involute_2', 'trochoid_2', 'lower_arc']:
            for x, y in tooth_profile[part_name]:
                # Rotate point
                cos_a = math.cos(rotation_angle)
                sin_a = math.sin(rotation_angle)
                x_rot = x * cos_a - y * sin_a
                y_rot = x * sin_a + y * cos_a
                full_gear_points.append((x_rot, y_rot))
    
    return full_gear_points

# Generate complete gear
gear_points = create_full_gear(profile, profile['parameters']['z'])
```

## Common Use Cases

### Standard Gear
```python
profile = generate_tooth_profile(z=24, m=2.0, alpha_deg=20.0)
```

### High Precision Gear  
```python
profile = generate_tooth_profile(z=24, m=2.0, alpha_deg=20.0, num_points=100)
```

### Gear with Profile Shift
```python
profile = generate_tooth_profile(z=24, m=2.0, alpha_deg=20.0, profile_shift=0.3)
```

### Small Gear with Undercut Prevention
```python
profile = generate_tooth_profile(z=8, m=2.0, alpha_deg=20.0, undercut_auto_suppress=True)
```

## Dependencies

- **Python standard library only**: `math`
- **For visualization examples**: `matplotlib` (optional)

## Files

- `gear_profile.py` - Main function implementation
- `test_gear_profile.py` - Usage examples without matplotlib
- `gear_profile_example.py` - Full visualization example with matplotlib

## Notes

- All coordinates are in mm if module is specified in mm
- The function handles edge cases like undercut conditions
- Profile shift positive values make teeth thicker, negative values make them thinner
- The function is optimized for CAD integration with minimal dependencies
