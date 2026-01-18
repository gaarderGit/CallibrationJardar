"""
Calibration module for performing various calibration calculations.
"""

import numpy as np


class LinearCalibration:
    """
    Linear calibration using the formula: y = mx + b
    """
    
    def __init__(self):
        self.slope = None
        self.intercept = None
    
    def fit(self, x_values, y_values):
        """
        Fit a linear calibration curve to the data.
        
        Args:
            x_values: Array-like of independent variable values
            y_values: Array-like of dependent variable values
        """
        x_values = np.array(x_values)
        y_values = np.array(y_values)
        
        # Calculate slope and intercept using least squares
        self.slope, self.intercept = np.polyfit(x_values, y_values, 1)
    
    def predict(self, x_values):
        """
        Predict calibrated values.
        
        Args:
            x_values: Array-like of values to calibrate
            
        Returns:
            Calibrated values
        """
        if self.slope is None or self.intercept is None:
            raise ValueError("Calibration not fitted. Call fit() first.")
        
        x_values = np.array(x_values)
        return self.slope * x_values + self.intercept
    
    def get_parameters(self):
        """
        Get calibration parameters.
        
        Returns:
            Dictionary with slope and intercept
        """
        return {
            "slope": self.slope,
            "intercept": self.intercept
        }


class PolynomialCalibration:
    """
    Polynomial calibration using nth degree polynomial.
    """
    
    def __init__(self, degree=2):
        """
        Initialize polynomial calibration.
        
        Args:
            degree: Degree of the polynomial (default: 2)
        """
        self.degree = degree
        self.coefficients = None
    
    def fit(self, x_values, y_values):
        """
        Fit a polynomial calibration curve to the data.
        
        Args:
            x_values: Array-like of independent variable values
            y_values: Array-like of dependent variable values
        """
        x_values = np.array(x_values)
        y_values = np.array(y_values)
        
        # Calculate coefficients using least squares
        self.coefficients = np.polyfit(x_values, y_values, self.degree)
    
    def predict(self, x_values):
        """
        Predict calibrated values.
        
        Args:
            x_values: Array-like of values to calibrate
            
        Returns:
            Calibrated values
        """
        if self.coefficients is None:
            raise ValueError("Calibration not fitted. Call fit() first.")
        
        x_values = np.array(x_values)
        return np.polyval(self.coefficients, x_values)
    
    def get_parameters(self):
        """
        Get calibration parameters.
        
        Returns:
            Dictionary with coefficients
        """
        return {
            "degree": self.degree,
            "coefficients": self.coefficients.tolist() if self.coefficients is not None else None
        }
