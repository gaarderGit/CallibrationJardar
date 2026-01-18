# Sample Data Files

This directory contains sample calibration data files that demonstrate the format and structure used by the CallibrationJardar package.

## Files

### sample_constants.json
Example calibration constants file showing:
- Temperature sensor calibration (offset, slope, reference)
- Pressure sensor calibration (atmospheric pressure, offset, scale factor)
- Flow meter calibration (K-factor, offset)

### sample_timeseries.json
Example timeseries calibration file showing:
- Monthly drift correction values over a year
- Temperature drift compensation data

## Usage

These files can be loaded directly into the package:

```python
from callibration import CalibrationConstants, TimeSeriesCalibration

# Load constants
constants = CalibrationConstants.from_json("data/sample_constants.json")

# Load timeseries
import json
with open("data/sample_timeseries.json", "r") as f:
    data = json.load(f)
timeseries = TimeSeriesCalibration.from_dict(data)
```

## File Formats

### Constants Format
```json
{
  "metadata": {
    "version": "string",
    "description": "string",
    "created_at": "ISO-8601 timestamp",
    "last_modified": "ISO-8601 timestamp"
  },
  "constants": {
    "category_name": {
      "constant_name": {
        "value": number,
        "unit": "string",
        "description": "string",
        "added_at": "ISO-8601 timestamp"
      }
    }
  }
}
```

### Timeseries Format
```json
{
  "name": "string",
  "unit": "string",
  "data": [
    {
      "timestamp": "ISO-8601 timestamp",
      "value": number
    }
  ]
}
```
