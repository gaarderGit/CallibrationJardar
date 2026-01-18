"""
Tests for the calibration module.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from callibration import LinearCalibration, PolynomialCalibration
import numpy as np


def test_linear_calibration():
    """Test linear calibration."""
    print("Testing Linear Calibration...")
    
    # Test data
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    y = [2.0, 4.0, 6.0, 8.0, 10.0]
    
    # Create and fit
    cal = LinearCalibration()
    cal.fit(x, y)
    
    # Check parameters
    params = cal.get_parameters()
    assert abs(params['slope'] - 2.0) < 0.01, f"Expected slope ~2.0, got {params['slope']}"
    assert abs(params['intercept'] - 0.0) < 0.01, f"Expected intercept ~0.0, got {params['intercept']}"
    
    # Test prediction
    pred = cal.predict([3.0])
    assert abs(pred[0] - 6.0) < 0.01, f"Expected prediction ~6.0, got {pred[0]}"
    
    print("✓ Linear calibration test passed")


def test_polynomial_calibration():
    """Test polynomial calibration."""
    print("Testing Polynomial Calibration...")
    
    # Test data: y = x^2
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    y = [1.0, 4.0, 9.0, 16.0, 25.0]
    
    # Create and fit
    cal = PolynomialCalibration(degree=2)
    cal.fit(x, y)
    
    # Test prediction
    pred = cal.predict([3.0])
    assert abs(pred[0] - 9.0) < 0.1, f"Expected prediction ~9.0, got {pred[0]}"
    
    print("✓ Polynomial calibration test passed")


def test_unfitted_error():
    """Test that unfitted calibration raises error."""
    print("Testing unfitted error handling...")
    
    cal = LinearCalibration()
    
    try:
        cal.predict([1.0])
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "not fitted" in str(e).lower()
    
    print("✓ Unfitted error test passed")


if __name__ == "__main__":
    test_linear_calibration()
    test_polynomial_calibration()
    test_unfitted_error()
    print("\nAll tests passed! ✓")
