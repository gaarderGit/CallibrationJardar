# CallibrationJardar

Calibration Code, and plants, established by Jardar Bond

A Python package for performing calibration calculations on sensor data and measurements.

## Features

- **Linear Calibration**: Simple linear calibration using least squares fitting
- **Polynomial Calibration**: Higher-order polynomial calibration for non-linear relationships

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or install the package:

```bash
pip install -e .
```

## Usage

### Linear Calibration

```python
from callibration import LinearCalibration

# Sample data
sensor_readings = [1.0, 2.0, 3.0, 4.0, 5.0]
actual_values = [2.1, 4.2, 6.1, 8.0, 10.1]

# Create and fit calibration
cal = LinearCalibration()
cal.fit(sensor_readings, actual_values)

# Predict new values
new_readings = [2.5, 3.5, 4.5]
calibrated = cal.predict(new_readings)
```

### Polynomial Calibration

```python
from callibration import PolynomialCalibration

# Sample data with non-linear relationship
sensor_readings = [1.0, 2.0, 3.0, 4.0, 5.0]
actual_values = [1.5, 4.5, 10.0, 18.0, 28.5]

# Create and fit calibration (degree 2)
cal = PolynomialCalibration(degree=2)
cal.fit(sensor_readings, actual_values)

# Predict new values
new_readings = [2.5, 3.5, 4.5]
calibrated = cal.predict(new_readings)
```

## Example

Run the example script to see the calibration in action:

```bash
python example.py
```

## Requirements

- Python 3.7+
- NumPy 1.20+
