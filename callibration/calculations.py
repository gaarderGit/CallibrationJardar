"""
Calculations module for performing measurement calculations with calibration data.

This module provides classes and functions for applying calibration data to
raw measurements and performing various measurement calculations.
"""

from typing import Optional, Union, List
import numpy as np
from datetime import datetime

from callibration.constants import CalibrationConstants
from callibration.timeseries import TimeSeriesCalibration


class MeasurementCalculator:
    """
    Performs measurement calculations using calibration data.
    
    This class applies calibration constants and timeseries data to raw
    measurements to produce calibrated results.
    
    Attributes:
        constants (CalibrationConstants): Calibration constants to use
        timeseries (Dict): Dictionary of timeseries calibrations by name
    """
    
    def __init__(self, constants: Optional[CalibrationConstants] = None):
        """
        Initialize the measurement calculator.
        
        Args:
            constants: CalibrationConstants instance to use for calculations
        """
        self.constants = constants if constants else CalibrationConstants()
        self.timeseries: dict[str, TimeSeriesCalibration] = {}
    
    def add_timeseries(self, timeseries: TimeSeriesCalibration) -> None:
        """
        Add a timeseries calibration to the calculator.
        
        Args:
            timeseries: TimeSeriesCalibration instance to add
        """
        self.timeseries[timeseries.name] = timeseries
    
    def apply_linear_calibration(self, raw_value: float, slope: float, 
                                 offset: float) -> float:
        """
        Apply a linear calibration: calibrated = slope * raw + offset
        
        Args:
            raw_value: Raw measurement value
            slope: Calibration slope
            offset: Calibration offset
        
        Returns:
            Calibrated value
        """
        return slope * raw_value + offset
    
    def apply_polynomial_calibration(self, raw_value: float, 
                                     coefficients: List[float]) -> float:
        """
        Apply polynomial calibration: calibrated = sum(coef[i] * raw^i)
        
        Args:
            raw_value: Raw measurement value
            coefficients: List of polynomial coefficients [c0, c1, c2, ...]
        
        Returns:
            Calibrated value
        """
        result = 0.0
        for i, coef in enumerate(coefficients):
            result += coef * (raw_value ** i)
        return result
    
    def calibrate_with_constant(self, raw_value: float, category: str, 
                                constant_name: str, operation: str = 'multiply') -> Optional[float]:
        """
        Calibrate a value using a stored constant.
        
        Args:
            raw_value: Raw measurement value
            category: Category of the calibration constant
            constant_name: Name of the calibration constant
            operation: Operation to perform ('multiply', 'add', 'divide', 'subtract')
        
        Returns:
            Calibrated value, or None if constant not found
        """
        constant_value = self.constants.get_constant(category, constant_name)
        if constant_value is None:
            return None
        
        if operation == 'multiply':
            return raw_value * constant_value
        elif operation == 'add':
            return raw_value + constant_value
        elif operation == 'divide':
            if constant_value == 0:
                raise ValueError("Cannot divide by zero")
            return raw_value / constant_value
        elif operation == 'subtract':
            return raw_value - constant_value
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def calibrate_with_timeseries(self, raw_value: float, timeseries_name: str,
                                  timestamp: datetime, operation: str = 'multiply',
                                  method: str = 'nearest') -> Optional[float]:
        """
        Calibrate a value using a timeseries calibration.
        
        Args:
            raw_value: Raw measurement value
            timeseries_name: Name of the timeseries to use
            timestamp: Time of the measurement
            operation: Operation to perform ('multiply', 'add', 'divide', 'subtract')
            method: Interpolation method for timeseries ('nearest', 'linear', etc.)
        
        Returns:
            Calibrated value, or None if timeseries not found or no data
        """
        if timeseries_name not in self.timeseries:
            return None
        
        ts = self.timeseries[timeseries_name]
        cal_value = ts.get_calibration_at_time(timestamp, method=method)
        
        if cal_value is None:
            return None
        
        if operation == 'multiply':
            return raw_value * cal_value
        elif operation == 'add':
            return raw_value + cal_value
        elif operation == 'divide':
            if cal_value == 0:
                raise ValueError("Cannot divide by zero")
            return raw_value / cal_value
        elif operation == 'subtract':
            return raw_value - cal_value
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def calibrate_series(self, raw_values: Union[List[float], np.ndarray],
                        slope: float, offset: float) -> np.ndarray:
        """
        Apply linear calibration to a series of values.
        
        Args:
            raw_values: Array or list of raw measurement values
            slope: Calibration slope
            offset: Calibration offset
        
        Returns:
            Array of calibrated values
        """
        raw_array = np.array(raw_values)
        return slope * raw_array + offset
    
    def calculate_moving_average(self, values: Union[List[float], np.ndarray],
                                window_size: int) -> np.ndarray:
        """
        Calculate moving average of a data series.
        
        Args:
            values: Array or list of values
            window_size: Size of the moving average window
        
        Returns:
            Array of moving average values
        """
        values_array = np.array(values)
        if window_size > len(values_array):
            raise ValueError("Window size cannot be larger than data length")
        
        cumsum = np.cumsum(np.insert(values_array, 0, 0))
        return (cumsum[window_size:] - cumsum[:-window_size]) / window_size
    
    def calculate_uncertainty(self, measured_value: float, 
                            systematic_error: float = 0.0,
                            random_error: float = 0.0) -> float:
        """
        Calculate total measurement uncertainty.
        
        Args:
            measured_value: The measured value
            systematic_error: Systematic error component
            random_error: Random error component
        
        Returns:
            Combined uncertainty
        """
        return np.sqrt(systematic_error**2 + random_error**2)
