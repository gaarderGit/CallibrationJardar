# Timeseries Calibration Documentation

This document describes the timeseries calibration functionality in the CallibrationJardar package.

## Overview

Timeseries calibration allows you to manage calibration values that change over time. This is essential for:
- Sensors with drift over time
- Seasonal calibration adjustments
- Equipment that requires periodic recalibration
- Environmental factors affecting measurements

## Features

- **Time-based storage**: Store calibration values with timestamps
- **Multiple interpolation methods**: Choose how to handle times between calibration points
- **Data import/export**: Save and load calibration data
- **Easy querying**: Get calibration values at any timestamp

## Interpolation Methods

### Nearest
Returns the calibration value from the closest timestamp.

```python
value = ts.get_calibration_at_time(timestamp, method='nearest')
```

**Use case**: When calibration doesn't change gradually between points.

### Linear
Interpolates linearly between calibration points.

```python
value = ts.get_calibration_at_time(timestamp, method='linear')
```

**Use case**: When calibration changes gradually over time.

### Forward
Returns the next calibration value (forward fill).

```python
value = ts.get_calibration_at_time(timestamp, method='forward')
```

**Use case**: When a calibration is valid from its timestamp onwards.

### Backward
Returns the previous calibration value (backward fill).

```python
value = ts.get_calibration_at_time(timestamp, method='backward')
```

**Use case**: When you want to use the most recent past calibration.

## Usage Examples

### Creating a Timeseries

```python
from callibration import TimeSeriesCalibration
from datetime import datetime

# Create a new timeseries
ts = TimeSeriesCalibration(name="sensor_gain", unit="V/V")

# Add calibration points
ts.add_calibration_point(datetime(2026, 1, 1), 1.000)
ts.add_calibration_point(datetime(2026, 2, 1), 1.002)
ts.add_calibration_point(datetime(2026, 3, 1), 1.005)
```

### Querying Calibration Values

```python
# Get calibration at a specific time
measurement_time = datetime(2026, 1, 15)
gain = ts.get_calibration_at_time(measurement_time, method='linear')

# Apply calibration to a measurement
raw_value = 10.5
calibrated_value = raw_value * gain
```

### Exporting and Importing

```python
# Export to dictionary
data_dict = ts.to_dict()

# Import from dictionary
ts_loaded = TimeSeriesCalibration.from_dict(data_dict)

# Get all data as DataFrame
df = ts.get_all_data()
```

## Data Structure

Timeseries data is stored as a pandas DataFrame with two columns:
- **timestamp**: datetime64[ns] - Time of calibration point
- **value**: float64 - Calibration value

## Best Practices

1. **Regular Updates**: Add calibration points at regular intervals
2. **Documentation**: Keep notes about why calibration values changed
3. **Validation**: Verify calibration points after adding them
4. **Backups**: Save timeseries data to files regularly
5. **Appropriate Methods**: Choose the right interpolation method for your use case
6. **Time Zones**: Be consistent with time zone handling

## Example: Complete Workflow

```python
from callibration import TimeSeriesCalibration, MeasurementCalculator
from datetime import datetime

# 1. Create timeseries
ts = TimeSeriesCalibration(name="pressure_offset", unit="Pa")

# 2. Add calibration data
ts.add_calibration_point(datetime(2026, 1, 1), 100.0)
ts.add_calibration_point(datetime(2026, 1, 15), 102.0)
ts.add_calibration_point(datetime(2026, 2, 1), 105.0)

# 3. Create calculator and add timeseries
calculator = MeasurementCalculator()
calculator.add_timeseries(ts)

# 4. Calibrate a measurement
measurement_time = datetime(2026, 1, 20)
raw_pressure = 1000.0
calibrated = calculator.calibrate_with_timeseries(
    raw_pressure, 
    "pressure_offset", 
    measurement_time, 
    operation='add',
    method='linear'
)

print(f"Raw: {raw_pressure} Pa, Calibrated: {calibrated} Pa")
```

## Timeseries File Format

Timeseries can be saved in JSON format:

```json
{
  "name": "sensor_gain",
  "unit": "V/V",
  "data": [
    {
      "timestamp": "2026-01-01T00:00:00",
      "value": 1.000
    },
    {
      "timestamp": "2026-02-01T00:00:00",
      "value": 1.002
    },
    {
      "timestamp": "2026-03-01T00:00:00",
      "value": 1.005
    }
  ]
}
```
