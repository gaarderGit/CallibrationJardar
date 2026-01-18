"""
Basic usage example of the CallibrationJardar package.

This example demonstrates:
1. Creating calibration constants
2. Creating a timeseries calibration
3. Using the measurement calculator
4. Processing measurements with calibration
"""

from callibration import (
    CalibrationConstants,
    TimeSeriesCalibration,
    MeasurementCalculator
)
from datetime import datetime


def main():
    print("=== CallibrationJardar Basic Usage Example ===\n")
    
    # 1. Create calibration constants
    print("1. Setting up calibration constants...")
    constants = CalibrationConstants(
        version="1.0.0",
        description="Example sensor calibration constants"
    )
    
    # Add temperature calibration constants
    constants.add_constant(
        category="temperature",
        name="offset",
        value=-0.5,
        unit="°C",
        description="Temperature sensor offset correction"
    )
    
    constants.add_constant(
        category="temperature",
        name="slope",
        value=1.01,
        unit="dimensionless",
        description="Temperature sensor slope correction"
    )
    
    print(f"   Added constants: {constants.list_categories()}")
    print(f"   Temperature offset: {constants.get_constant('temperature', 'offset')}°C")
    print(f"   Temperature slope: {constants.get_constant('temperature', 'slope')}\n")
    
    # 2. Create a timeseries calibration for drift
    print("2. Setting up timeseries for drift correction...")
    drift = TimeSeriesCalibration(name="temp_drift", unit="°C")
    
    # Add calibration points over time
    drift.add_calibration_point(datetime(2026, 1, 1), 0.0)
    drift.add_calibration_point(datetime(2026, 1, 15), 0.1)
    drift.add_calibration_point(datetime(2026, 2, 1), 0.2)
    drift.add_calibration_point(datetime(2026, 2, 15), 0.3)
    
    print(f"   Added {len(drift.get_all_data())} calibration points")
    print(f"   Drift at 2026-01-01: {drift.get_calibration_at_time(datetime(2026, 1, 1))}°C")
    print(f"   Drift at 2026-02-15: {drift.get_calibration_at_time(datetime(2026, 2, 15))}°C\n")
    
    # 3. Create measurement calculator
    print("3. Creating measurement calculator...")
    calculator = MeasurementCalculator(constants)
    calculator.add_timeseries(drift)
    print("   Calculator ready with constants and timeseries\n")
    
    # 4. Process a measurement
    print("4. Processing a temperature measurement...")
    raw_temperature = 25.5
    measurement_time = datetime(2026, 1, 20)
    
    print(f"   Raw measurement: {raw_temperature}°C at {measurement_time}")
    
    # Apply linear calibration
    temp_with_cal = calculator.apply_linear_calibration(
        raw_value=raw_temperature,
        slope=constants.get_constant("temperature", "slope"),
        offset=constants.get_constant("temperature", "offset")
    )
    print(f"   After linear calibration: {temp_with_cal:.3f}°C")
    
    # Apply drift correction
    temp_final = calculator.calibrate_with_timeseries(
        raw_value=temp_with_cal,
        timeseries_name="temp_drift",
        timestamp=measurement_time,
        operation='add',
        method='linear'
    )
    print(f"   After drift correction: {temp_final:.3f}°C")
    
    # Calculate uncertainty
    uncertainty = calculator.calculate_uncertainty(
        measured_value=temp_final,
        systematic_error=0.1,
        random_error=0.05
    )
    print(f"   Measurement uncertainty: ±{uncertainty:.3f}°C")
    print(f"   Final result: {temp_final:.3f} ± {uncertainty:.3f}°C\n")
    
    # 5. Process a series of measurements
    print("5. Processing multiple measurements...")
    raw_values = [25.5, 26.0, 25.8, 26.2, 25.9, 26.1, 25.7]
    print(f"   Raw values: {raw_values}")
    
    calibrated_series = calculator.calibrate_series(
        raw_values=raw_values,
        slope=constants.get_constant("temperature", "slope"),
        offset=constants.get_constant("temperature", "offset")
    )
    print(f"   Calibrated values: {[f'{v:.2f}' for v in calibrated_series]}")
    
    # Calculate moving average
    smoothed = calculator.calculate_moving_average(calibrated_series, window_size=3)
    print(f"   Smoothed (MA-3): {[f'{v:.2f}' for v in smoothed]}\n")
    
    # 6. Save calibration data
    print("6. Saving calibration data...")
    constants.to_json("example_constants.json")
    print("   Saved constants to: example_constants.json")
    
    # Export timeseries
    import json
    with open("example_timeseries.json", "w") as f:
        json.dump(drift.to_dict(), f, indent=2)
    print("   Saved timeseries to: example_timeseries.json")
    
    print("\n=== Example completed successfully! ===")


if __name__ == "__main__":
    main()
