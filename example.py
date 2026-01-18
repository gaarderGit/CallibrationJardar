#!/usr/bin/env python3
"""
Example script demonstrating the usage of the calibration module.
"""

from callibration import LinearCalibration, PolynomialCalibration


def linear_example():
    """Demonstrate linear calibration."""
    print("=" * 50)
    print("Linear Calibration Example")
    print("=" * 50)
    
    # Sample data: sensor readings vs actual values
    sensor_readings = [1.0, 2.0, 3.0, 4.0, 5.0]
    actual_values = [2.1, 4.2, 6.1, 8.0, 10.1]
    
    # Create and fit calibration
    cal = LinearCalibration()
    cal.fit(sensor_readings, actual_values)
    
    # Get parameters
    params = cal.get_parameters()
    print(f"Slope: {params['slope']:.4f}")
    print(f"Intercept: {params['intercept']:.4f}")
    
    # Predict new values
    new_readings = [2.5, 3.5, 4.5]
    calibrated = cal.predict(new_readings)
    
    print("\nCalibration Results:")
    for reading, result in zip(new_readings, calibrated):
        print(f"  Sensor: {reading:.1f} -> Calibrated: {result:.2f}")
    print()


def polynomial_example():
    """Demonstrate polynomial calibration."""
    print("=" * 50)
    print("Polynomial Calibration Example (Degree 2)")
    print("=" * 50)
    
    # Sample data with non-linear relationship
    sensor_readings = [1.0, 2.0, 3.0, 4.0, 5.0]
    actual_values = [1.5, 4.5, 10.0, 18.0, 28.5]
    
    # Create and fit calibration
    cal = PolynomialCalibration(degree=2)
    cal.fit(sensor_readings, actual_values)
    
    # Get parameters
    params = cal.get_parameters()
    print(f"Degree: {params['degree']}")
    print(f"Coefficients: {params['coefficients']}")
    
    # Predict new values
    new_readings = [2.5, 3.5, 4.5]
    calibrated = cal.predict(new_readings)
    
    print("\nCalibration Results:")
    for reading, result in zip(new_readings, calibrated):
        print(f"  Sensor: {reading:.1f} -> Calibrated: {result:.2f}")
    print()


if __name__ == "__main__":
    linear_example()
    polynomial_example()
