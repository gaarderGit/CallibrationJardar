"""
Advanced example showing sensor calibration workflow.

This example demonstrates:
1. Multi-stage calibration pipeline
2. Working with different sensor types
3. Time-based calibration selection
4. Data quality checks
"""

from callibration import (
    CalibrationConstants,
    TimeSeriesCalibration,
    MeasurementCalculator
)
from datetime import datetime, timedelta
import numpy as np


class SensorCalibrationPipeline:
    """Complete calibration pipeline for sensor data."""
    
    def __init__(self):
        self.constants = CalibrationConstants(
            version="2.0.0",
            description="Multi-sensor calibration system"
        )
        self.calculator = MeasurementCalculator(self.constants)
        self.setup_calibrations()
    
    def setup_calibrations(self):
        """Setup all calibration constants and timeseries."""
        # Temperature sensor calibration
        self.constants.add_constant("temperature", "offset", -0.3, "°C",
                                   "Offset from reference thermometer")
        self.constants.add_constant("temperature", "slope", 0.998, "",
                                   "Slope correction factor")
        
        # Pressure sensor calibration
        self.constants.add_constant("pressure", "zero_offset", 101325, "Pa",
                                   "Atmospheric pressure offset")
        self.constants.add_constant("pressure", "sensitivity", 1.005, "",
                                   "Sensor sensitivity factor")
        
        # Flow sensor calibration
        self.constants.add_constant("flow", "k_factor", 450, "pulses/L",
                                   "Flow meter K-factor")
        
        # Setup timeseries for temperature drift
        temp_drift = TimeSeriesCalibration("temp_drift", "°C")
        base_date = datetime(2026, 1, 1)
        for i in range(12):  # 12 months
            date = base_date + timedelta(days=30*i)
            drift_value = 0.02 * i  # Increasing drift over time
            temp_drift.add_calibration_point(date, drift_value)
        
        self.calculator.add_timeseries(temp_drift)
        
        # Setup timeseries for pressure drift
        pressure_drift = TimeSeriesCalibration("pressure_drift", "Pa")
        for i in range(12):
            date = base_date + timedelta(days=30*i)
            drift_value = 10 * i  # Increasing drift
            pressure_drift.add_calibration_point(date, drift_value)
        
        self.calculator.add_timeseries(pressure_drift)
    
    def calibrate_temperature(self, raw_value, timestamp):
        """Calibrate temperature measurement."""
        # Step 1: Apply linear calibration
        slope = self.constants.get_constant("temperature", "slope")
        offset = self.constants.get_constant("temperature", "offset")
        temp = self.calculator.apply_linear_calibration(raw_value, slope, offset)
        
        # Step 2: Apply drift correction
        temp = self.calculator.calibrate_with_timeseries(
            temp, "temp_drift", timestamp, operation='add', method='linear'
        )
        
        return temp
    
    def calibrate_pressure(self, raw_value, timestamp):
        """Calibrate pressure measurement."""
        # Step 1: Apply sensitivity
        sensitivity = self.constants.get_constant("pressure", "sensitivity")
        pressure = raw_value * sensitivity
        
        # Step 2: Apply zero offset
        zero_offset = self.constants.get_constant("pressure", "zero_offset")
        pressure = pressure - zero_offset
        
        # Step 3: Apply drift correction
        pressure = self.calculator.calibrate_with_timeseries(
            pressure, "pressure_drift", timestamp, operation='add', method='linear'
        )
        
        return pressure
    
    def calibrate_flow(self, pulse_count, duration_seconds):
        """Calibrate flow measurement from pulse counter."""
        k_factor = self.constants.get_constant("flow", "k_factor")
        volume_liters = pulse_count / k_factor
        flow_rate = volume_liters / duration_seconds * 3600  # L/hour
        return flow_rate
    
    def process_sensor_data(self, sensor_data):
        """Process a batch of sensor readings."""
        results = []
        
        for reading in sensor_data:
            sensor_type = reading['type']
            timestamp = reading['timestamp']
            raw_value = reading['raw_value']
            
            if sensor_type == 'temperature':
                calibrated = self.calibrate_temperature(raw_value, timestamp)
                unit = '°C'
            elif sensor_type == 'pressure':
                calibrated = self.calibrate_pressure(raw_value, timestamp)
                unit = 'Pa'
            elif sensor_type == 'flow':
                duration = reading.get('duration', 1.0)
                calibrated = self.calibrate_flow(raw_value, duration)
                unit = 'L/hour'
            else:
                calibrated = raw_value
                unit = 'unknown'
            
            results.append({
                'timestamp': timestamp,
                'type': sensor_type,
                'raw': raw_value,
                'calibrated': calibrated,
                'unit': unit
            })
        
        return results


def main():
    print("=== Advanced Sensor Calibration Pipeline Example ===\n")
    
    # Create calibration pipeline
    pipeline = SensorCalibrationPipeline()
    print("Calibration pipeline initialized\n")
    
    # Simulate sensor data over time
    print("Processing sensor readings...\n")
    
    sensor_data = [
        {
            'type': 'temperature',
            'timestamp': datetime(2026, 1, 15),
            'raw_value': 22.5
        },
        {
            'type': 'temperature',
            'timestamp': datetime(2026, 6, 15),
            'raw_value': 28.3
        },
        {
            'type': 'pressure',
            'timestamp': datetime(2026, 1, 15),
            'raw_value': 105000
        },
        {
            'type': 'pressure',
            'timestamp': datetime(2026, 6, 15),
            'raw_value': 103000
        },
        {
            'type': 'flow',
            'timestamp': datetime(2026, 1, 15),
            'raw_value': 4500,  # pulse count
            'duration': 10.0    # seconds
        }
    ]
    
    # Process all readings
    results = pipeline.process_sensor_data(sensor_data)
    
    # Display results
    for result in results:
        print(f"{result['type'].upper()} Measurement:")
        print(f"  Timestamp: {result['timestamp']}")
        print(f"  Raw value: {result['raw']}")
        print(f"  Calibrated: {result['calibrated']:.2f} {result['unit']}")
        print()
    
    # Demonstrate batch processing with moving average
    print("Batch processing with noise reduction...\n")
    
    raw_temps = [22.1, 22.5, 22.3, 22.8, 22.4, 22.6, 22.9, 22.7]
    timestamp = datetime(2026, 3, 1)
    
    print(f"Raw temperatures: {raw_temps}")
    
    # Calibrate all values
    calibrated_temps = [
        pipeline.calibrate_temperature(temp, timestamp)
        for temp in raw_temps
    ]
    print(f"Calibrated: {[f'{t:.2f}' for t in calibrated_temps]}")
    
    # Apply moving average
    smoothed = pipeline.calculator.calculate_moving_average(
        calibrated_temps, window_size=3
    )
    print(f"Smoothed (MA-3): {[f'{t:.2f}' for t in smoothed]}")
    
    print("\n=== Advanced example completed successfully! ===")


if __name__ == "__main__":
    main()
