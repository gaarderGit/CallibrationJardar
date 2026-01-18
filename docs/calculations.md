# Measurement Calculations Documentation

This document describes the measurement calculation capabilities in the CallibrationJardar package.

## Overview

The `MeasurementCalculator` class provides various methods for applying calibrations to measurements and performing data series calculations.

## Calibration Methods

### Linear Calibration

Apply a simple linear calibration: `calibrated = slope * raw + offset`

```python
from callibration import MeasurementCalculator

calculator = MeasurementCalculator()
calibrated = calculator.apply_linear_calibration(
    raw_value=100.0,
    slope=1.05,
    offset=2.0
)
# Result: 100.0 * 1.05 + 2.0 = 107.0
```

**Use case**: Most common calibration for linear sensors.

### Polynomial Calibration

Apply polynomial calibration: `calibrated = c0 + c1*raw + c2*raw² + ...`

```python
calibrated = calculator.apply_polynomial_calibration(
    raw_value=10.0,
    coefficients=[1.0, 2.0, 0.5]  # c0, c1, c2
)
# Result: 1.0 + 2.0*10.0 + 0.5*10.0² = 1.0 + 20.0 + 50.0 = 71.0
```

**Use case**: Non-linear sensors or complex calibration curves.

### Constant-Based Calibration

Apply calibration using stored constants:

```python
from callibration import CalibrationConstants, MeasurementCalculator

# Setup constants
constants = CalibrationConstants()
constants.add_constant("pressure", "scale_factor", 1.05, "Pa/Pa")

# Use in calculator
calculator = MeasurementCalculator(constants)
calibrated = calculator.calibrate_with_constant(
    raw_value=1000.0,
    category="pressure",
    constant_name="scale_factor",
    operation='multiply'
)
# Result: 1000.0 * 1.05 = 1050.0
```

**Operations**: 'multiply', 'add', 'divide', 'subtract'

### Timeseries-Based Calibration

Apply calibration using time-varying values:

```python
from callibration import TimeSeriesCalibration, MeasurementCalculator
from datetime import datetime

# Setup timeseries
ts = TimeSeriesCalibration("drift_correction", "")
ts.add_calibration_point(datetime(2026, 1, 1), 1.00)
ts.add_calibration_point(datetime(2026, 2, 1), 1.02)

# Use in calculator
calculator = MeasurementCalculator()
calculator.add_timeseries(ts)

calibrated = calculator.calibrate_with_timeseries(
    raw_value=100.0,
    timeseries_name="drift_correction",
    timestamp=datetime(2026, 1, 15),
    operation='multiply',
    method='linear'
)
```

## Data Series Operations

### Series Calibration

Apply calibration to multiple values at once:

```python
import numpy as np

raw_values = [100.0, 101.0, 102.0, 103.0, 104.0]
calibrated = calculator.calibrate_series(
    raw_values=raw_values,
    slope=1.05,
    offset=2.0
)
# Result: array of calibrated values
```

**Benefit**: Efficient processing of large datasets using NumPy.

### Moving Average

Calculate moving average for smoothing data:

```python
values = [10, 12, 15, 14, 16, 18, 20, 19, 21, 23]
smoothed = calculator.calculate_moving_average(
    values=values,
    window_size=3
)
# Returns moving average with window size 3
```

**Use case**: Noise reduction in measurement data.

### Uncertainty Calculation

Calculate combined measurement uncertainty:

```python
uncertainty = calculator.calculate_uncertainty(
    measured_value=100.0,
    systematic_error=0.5,
    random_error=0.3
)
# Result: sqrt(0.5² + 0.3²) = 0.583
```

**Use case**: Determining measurement confidence intervals.

## Complete Example

```python
from callibration import (
    CalibrationConstants,
    TimeSeriesCalibration,
    MeasurementCalculator
)
from datetime import datetime
import numpy as np

# 1. Setup calibration constants
constants = CalibrationConstants(version="1.0.0")
constants.add_constant("temperature", "offset", -0.5, "°C")
constants.add_constant("temperature", "slope", 1.01, "")

# 2. Setup timeseries for drift correction
drift = TimeSeriesCalibration("temp_drift", "°C")
drift.add_calibration_point(datetime(2026, 1, 1), 0.0)
drift.add_calibration_point(datetime(2026, 1, 15), 0.2)
drift.add_calibration_point(datetime(2026, 2, 1), 0.4)

# 3. Create calculator
calc = MeasurementCalculator(constants)
calc.add_timeseries(drift)

# 4. Process a single measurement
raw_temp = 25.5
measurement_time = datetime(2026, 1, 10)

# Apply linear calibration
temp1 = calc.apply_linear_calibration(
    raw_temp,
    slope=constants.get_constant("temperature", "slope"),
    offset=constants.get_constant("temperature", "offset")
)

# Apply drift correction
temp2 = calc.calibrate_with_timeseries(
    temp1,
    "temp_drift",
    measurement_time,
    operation='add',
    method='linear'
)

print(f"Raw: {raw_temp}°C → Calibrated: {temp2:.2f}°C")

# 5. Process multiple measurements
raw_temps = [25.5, 26.0, 25.8, 26.2, 25.9]
slope = constants.get_constant("temperature", "slope")
offset = constants.get_constant("temperature", "offset")

calibrated_temps = calc.calibrate_series(raw_temps, slope, offset)

# 6. Calculate moving average
smoothed = calc.calculate_moving_average(calibrated_temps, window_size=3)

print(f"Smoothed data: {smoothed}")
```

## Best Practices

1. **Order of Operations**: Apply calibrations in the correct order (typically: offset → scale → drift)
2. **Validation**: Always validate calibrated values are within expected ranges
3. **Documentation**: Document which calibration method and constants are used
4. **Uncertainty**: Include uncertainty calculations for critical measurements
5. **Performance**: Use series operations for large datasets
6. **Testing**: Test calibration formulas with known values

## Common Calibration Workflows

### Workflow 1: Simple Linear Sensor
```
Raw Value → Linear Calibration (slope, offset) → Calibrated Value
```

### Workflow 2: Sensor with Drift
```
Raw Value → Linear Calibration → Drift Correction (timeseries) → Calibrated Value
```

### Workflow 3: Non-linear Sensor
```
Raw Value → Polynomial Calibration → Calibrated Value
```

### Workflow 4: Multi-stage Calibration
```
Raw Value → Hardware Calibration (constants) → 
Environmental Correction (timeseries) → 
Final Smoothing (moving average) → 
Calibrated Value
```
