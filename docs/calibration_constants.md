# Calibration Constants Documentation

This document describes the calibration constants used in the CallibrationJardar package for measurement calculations and data series.

## Overview

Calibration constants are fixed values used to convert raw measurements into calibrated, accurate measurements. These constants are typically determined through calibration procedures and remain valid for a specific period or until the next calibration.

## Constant Categories

The calibration constants are organized into categories for better management:

### Temperature Calibration

Constants related to temperature measurements and corrections.

- **offset**: Temperature offset value (°C)
- **slope**: Temperature slope for linear calibration
- **reference_temp**: Reference temperature for calibration (°C)

### Pressure Calibration

Constants related to pressure measurements.

- **atmospheric_pressure**: Standard atmospheric pressure (Pa)
- **sensor_offset**: Pressure sensor offset (Pa)
- **scale_factor**: Pressure scale factor

### Flow Rate Calibration

Constants for flow rate measurements.

- **k_factor**: Flow meter K-factor (pulses/L)
- **offset**: Flow meter offset
- **density_correction**: Fluid density correction factor

### General Calibration

General-purpose calibration constants.

- **gravity**: Standard gravitational acceleration (m/s²)
- **conversion_factor**: Generic conversion factor

## Constant Format

Each constant is stored with the following information:

```json
{
  "value": <numeric_value>,
  "unit": "<unit_of_measurement>",
  "description": "<description_of_constant>",
  "added_at": "<ISO_timestamp>"
}
```

## Using Constants in Code

Example of adding and using calibration constants:

```python
from callibration import CalibrationConstants

# Create constants instance
constants = CalibrationConstants(version="1.0.0", description="Sensor calibration 2026")

# Add constants
constants.add_constant(
    category="temperature",
    name="offset",
    value=0.5,
    unit="°C",
    description="Temperature sensor offset"
)

# Retrieve constant
offset = constants.get_constant("temperature", "offset")
```

## Version Control

Constants are versioned to track changes over time. Each set of constants includes:

- **version**: Semantic version number (e.g., "1.0.0")
- **description**: Description of the constant set
- **created_at**: Timestamp when constants were created
- **last_modified**: Timestamp of last modification

## Saving and Loading

Constants can be saved to and loaded from JSON files:

```python
# Save constants
constants.to_json("calibration_constants.json")

# Load constants
constants = CalibrationConstants.from_json("calibration_constants.json")
```

## Best Practices

1. **Version Management**: Always increment version numbers when updating constants
2. **Documentation**: Provide clear descriptions for each constant
3. **Units**: Always specify units of measurement
4. **Backup**: Keep backup copies of calibration constants
5. **Validation**: Verify constants after loading from files
6. **Traceability**: Document the source and date of calibration

## Example Calibration Constants File

```json
{
  "metadata": {
    "version": "1.0.0",
    "description": "Primary sensor calibration constants",
    "created_at": "2026-01-01T00:00:00",
    "last_modified": "2026-01-15T12:00:00"
  },
  "constants": {
    "temperature": {
      "offset": {
        "value": 0.5,
        "unit": "°C",
        "description": "Temperature sensor offset",
        "added_at": "2026-01-01T00:00:00"
      },
      "slope": {
        "value": 1.002,
        "unit": "dimensionless",
        "description": "Temperature slope correction",
        "added_at": "2026-01-01T00:00:00"
      }
    },
    "pressure": {
      "offset": {
        "value": 100.0,
        "unit": "Pa",
        "description": "Pressure sensor offset",
        "added_at": "2026-01-01T00:00:00"
      }
    }
  }
}
```
