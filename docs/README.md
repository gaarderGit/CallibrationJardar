# CallibrationJardar Documentation

Welcome to the CallibrationJardar documentation. This package provides tools for managing calibration data, constants, and performing measurement calculations.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Core Concepts](#core-concepts)
3. [API Documentation](#api-documentation)
4. [Examples](#examples)
5. [Best Practices](#best-practices)

## Getting Started

### Installation

```bash
pip install -r requirements.txt
```

### First Steps

1. Read the [Quick Start Guide](../README.md#quick-start)
2. Try the [Basic Usage Example](../examples/basic_usage.py)
3. Explore the API documentation below

## Core Concepts

### Calibration Constants

Calibration constants are fixed values used to convert raw measurements into calibrated values. They are:
- Organized by category (e.g., temperature, pressure, flow)
- Versioned for tracking changes
- Stored with metadata (units, descriptions, timestamps)

See [Calibration Constants Documentation](calibration_constants.md) for details.

### Timeseries Calibration

Timeseries calibrations handle values that change over time, such as:
- Sensor drift
- Seasonal adjustments
- Environmental corrections

See [Timeseries Documentation](timeseries.md) for details.

### Measurement Calculations

The calculation module provides tools to:
- Apply linear and polynomial calibrations
- Use constants and timeseries in calculations
- Process data series
- Calculate uncertainties

See [Calculations Documentation](calculations.md) for details.

## API Documentation

### CalibrationConstants Class

Main class for managing calibration constants.

**Methods:**
- `add_constant(category, name, value, unit, description)` - Add a new constant
- `get_constant(category, name)` - Retrieve a constant value
- `get_constant_info(category, name)` - Get complete constant information
- `list_categories()` - List all categories
- `list_constants_in_category(category)` - List constants in a category
- `to_json(filepath)` - Save constants to JSON file
- `from_json(filepath)` - Load constants from JSON file

### TimeSeriesCalibration Class

Main class for managing time-based calibration data.

**Methods:**
- `add_calibration_point(timestamp, value)` - Add a calibration point
- `get_calibration_at_time(timestamp, method)` - Query calibration at a time
- `get_all_data()` - Get all calibration data as DataFrame
- `to_dict()` - Export to dictionary
- `from_dict(data)` - Import from dictionary

**Interpolation Methods:**
- `nearest` - Use closest calibration point
- `linear` - Linear interpolation between points
- `forward` - Forward fill (next value)
- `backward` - Backward fill (previous value)

### MeasurementCalculator Class

Main class for applying calibrations to measurements.

**Methods:**
- `add_timeseries(timeseries)` - Add a timeseries calibration
- `apply_linear_calibration(raw_value, slope, offset)` - Linear calibration
- `apply_polynomial_calibration(raw_value, coefficients)` - Polynomial calibration
- `calibrate_with_constant(raw_value, category, name, operation)` - Use stored constant
- `calibrate_with_timeseries(raw_value, name, timestamp, operation, method)` - Use timeseries
- `calibrate_series(raw_values, slope, offset)` - Calibrate multiple values
- `calculate_moving_average(values, window_size)` - Moving average smoothing
- `calculate_uncertainty(measured_value, systematic_error, random_error)` - Uncertainty calculation

## Examples

### Example 1: Simple Temperature Calibration

```python
from callibration import MeasurementCalculator

calculator = MeasurementCalculator()
calibrated_temp = calculator.apply_linear_calibration(
    raw_value=25.5,
    slope=1.01,
    offset=-0.5
)
```

### Example 2: Using Constants

```python
from callibration import CalibrationConstants, MeasurementCalculator

constants = CalibrationConstants()
constants.add_constant("pressure", "scale", 1.05, "Pa/Pa")

calculator = MeasurementCalculator(constants)
calibrated = calculator.calibrate_with_constant(
    raw_value=1000.0,
    category="pressure",
    constant_name="scale",
    operation='multiply'
)
```

### Example 3: Time-Based Calibration

```python
from callibration import TimeSeriesCalibration, MeasurementCalculator
from datetime import datetime

ts = TimeSeriesCalibration("drift", "°C")
ts.add_calibration_point(datetime(2026, 1, 1), 0.0)
ts.add_calibration_point(datetime(2026, 2, 1), 0.2)

calculator = MeasurementCalculator()
calculator.add_timeseries(ts)

calibrated = calculator.calibrate_with_timeseries(
    raw_value=25.0,
    timeseries_name="drift",
    timestamp=datetime(2026, 1, 15),
    operation='add',
    method='linear'
)
```

For more examples, see the [examples directory](../examples/).

## Best Practices

### 1. Version Control
Always version your calibration constants and document changes.

```python
constants = CalibrationConstants(
    version="1.2.0",
    description="Updated pressure sensor calibration after maintenance"
)
```

### 2. Documentation
Provide clear descriptions for all constants and calibrations.

```python
constants.add_constant(
    category="temperature",
    name="offset",
    value=-0.5,
    unit="°C",
    description="Offset from NIST-traceable reference thermometer, calibration date: 2026-01-15"
)
```

### 3. Regular Backups
Save calibration data regularly to prevent data loss.

```python
constants.to_json(f"calibration_backup_{datetime.now().isoformat()}.json")
```

### 4. Validation
Always validate calibrated values are within expected ranges.

```python
calibrated = calculator.apply_linear_calibration(raw_value, slope, offset)
if not (expected_min <= calibrated <= expected_max):
    raise ValueError(f"Calibrated value {calibrated} outside expected range")
```

### 5. Uncertainty
Include uncertainty calculations for critical measurements.

```python
uncertainty = calculator.calculate_uncertainty(
    measured_value=value,
    systematic_error=0.1,
    random_error=0.05
)
print(f"Result: {value:.2f} ± {uncertainty:.2f}")
```

### 6. Choose Appropriate Interpolation
Select the right interpolation method for your use case:
- **nearest**: Calibration changes suddenly at specific times
- **linear**: Gradual drift between calibration points
- **forward**: Calibration valid from timestamp onwards
- **backward**: Use most recent past calibration

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/gaarderGit/CallibrationJardar/issues
- Documentation: This folder and subdocuments

## Additional Resources

- [Calibration Constants Details](calibration_constants.md)
- [Timeseries Calibration Guide](timeseries.md)
- [Measurement Calculations Guide](calculations.md)
- [Basic Usage Example](../examples/basic_usage.py)
- [Advanced Pipeline Example](../examples/advanced_calibration.py)
