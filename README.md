# CallibrationJardar

Repository for Python code for calibration timeseries, documentation and releases for information and new calibration constants related to measurement calculations and data series.

**Established by Jardar Bond**

## Overview

CallibrationJardar is a Python package designed to manage calibration data, constants, and perform measurement calculations for scientific and industrial applications. It provides a comprehensive framework for:

- **Timeseries Calibration**: Manage calibration values that change over time
- **Calibration Constants**: Store and retrieve versioned calibration constants
- **Measurement Calculations**: Apply calibrations to raw measurements
- **Data Series Analysis**: Process and analyze measurement data

## Features

### Timeseries Calibration
- Store calibration data with timestamps
- Multiple interpolation methods (nearest, linear, forward, backward)
- Import/export timeseries data
- Query calibration values at any time point

### Calibration Constants
- Organize constants by category
- Version control for calibration sets
- Store metadata (units, descriptions, timestamps)
- JSON import/export

### Measurement Calculations
- Linear and polynomial calibration
- Constant-based calibration
- Timeseries-based calibration
- Moving average calculation
- Uncertainty estimation

## Installation

### From Source
```bash
git clone https://github.com/gaarderGit/CallibrationJardar.git
cd CallibrationJardar
pip install -e .
```

### Dependencies
- Python >= 3.8
- numpy >= 1.20.0
- pandas >= 1.3.0

## Quick Start

### Basic Example

```python
from callibration import (
    CalibrationConstants,
    TimeSeriesCalibration,
    MeasurementCalculator
)
from datetime import datetime

# Create calibration constants
constants = CalibrationConstants(version="1.0.0")
constants.add_constant("temperature", "offset", -0.5, "°C")
constants.add_constant("temperature", "slope", 1.01, "")

# Create timeseries for drift correction
drift = TimeSeriesCalibration("temp_drift", "°C")
drift.add_calibration_point(datetime(2026, 1, 1), 0.0)
drift.add_calibration_point(datetime(2026, 2, 1), 0.2)

# Create calculator and apply calibration
calculator = MeasurementCalculator(constants)
calculator.add_timeseries(drift)

# Calibrate a measurement
raw_temp = 25.5
calibrated = calculator.apply_linear_calibration(
    raw_temp,
    slope=constants.get_constant("temperature", "slope"),
    offset=constants.get_constant("temperature", "offset")
)

print(f"Calibrated temperature: {calibrated}°C")
```

## Documentation

Detailed documentation is available in the `docs/` directory:

- [Calibration Constants](docs/calibration_constants.md) - Managing calibration constants
- [Timeseries Calibration](docs/timeseries.md) - Working with time-based calibration
- [Measurement Calculations](docs/calculations.md) - Applying calibrations and calculations

## Examples

Example scripts are provided in the `examples/` directory:

- `basic_usage.py` - Introduction to the package features
- `advanced_calibration.py` - Multi-sensor calibration pipeline

Run examples:
```bash
python examples/basic_usage.py
python examples/advanced_calibration.py
```

## Project Structure

```
CallibrationJardar/
├── callibration/           # Main package
│   ├── __init__.py        # Package initialization
│   ├── timeseries.py      # Timeseries calibration
│   ├── constants.py       # Calibration constants
│   └── calculations.py    # Measurement calculations
├── docs/                  # Documentation
│   ├── calibration_constants.md
│   ├── timeseries.md
│   └── calculations.md
├── examples/              # Usage examples
│   ├── basic_usage.py
│   └── advanced_calibration.py
├── pyproject.toml        # Project configuration
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## Development

### Running Tests
```bash
pip install -e ".[dev]"
pytest
```

### Code Formatting
```bash
black callibration/
```

### Linting
```bash
flake8 callibration/
```

## Use Cases

- **Laboratory Measurements**: Calibrate scientific instruments
- **Industrial Sensors**: Manage sensor calibrations in production
- **Environmental Monitoring**: Apply calibrations to environmental data
- **Quality Control**: Track calibration history and ensure data quality
- **IoT Applications**: Calibrate sensor data from IoT devices

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

MIT License

## Author

Jardar Bond

## Version

0.1.0

## Changelog

### Version 0.1.0 (2026-01-18)
- Initial release
- Timeseries calibration support
- Calibration constants management
- Measurement calculation tools
- Documentation and examples
