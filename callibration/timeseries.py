"""
Timeseries module for managing calibration data over time.

This module provides classes and functions for handling time-based calibration data,
including loading, storing, and querying calibration values at specific timestamps.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import pandas as pd


class TimeSeriesCalibration:
    """
    Manages calibration data as a timeseries.
    
    This class handles calibration values that change over time, allowing you to:
    - Store calibration data with timestamps
    - Query calibration values at specific times
    - Interpolate between calibration points
    - Export and import calibration timeseries
    
    Attributes:
        name (str): Name of the calibration timeseries
        data (pd.DataFrame): DataFrame containing timestamp and calibration values
    """
    
    def __init__(self, name: str, unit: str = ""):
        """
        Initialize a new timeseries calibration.
        
        Args:
            name: Name identifier for this calibration timeseries
            unit: Unit of measurement for the calibration values
        """
        self.name = name
        self.unit = unit
        self.data = pd.DataFrame(columns=['timestamp', 'value'])
        self.data = self.data.astype({'timestamp': 'datetime64[ns]', 'value': 'float64'})
    
    def add_calibration_point(self, timestamp: datetime, value: float) -> None:
        """
        Add a calibration point to the timeseries.
        
        Args:
            timestamp: Time when this calibration value is valid
            value: Calibration value at this timestamp
        """
        new_row = pd.DataFrame({
            'timestamp': [pd.Timestamp(timestamp)],
            'value': [value]
        })
        self.data = pd.concat([self.data, new_row], ignore_index=True)
        self.data = self.data.sort_values('timestamp').reset_index(drop=True)
    
    def get_calibration_at_time(self, timestamp: datetime, method: str = 'nearest') -> Optional[float]:
        """
        Get the calibration value at a specific time.
        
        Args:
            timestamp: Time to query the calibration value
            method: Interpolation method ('nearest', 'linear', 'forward', 'backward')
        
        Returns:
            Calibration value at the specified time, or None if no data available
        """
        if self.data.empty:
            return None
        
        query_time = pd.Timestamp(timestamp)
        
        if method == 'nearest':
            idx = (self.data['timestamp'] - query_time).abs().idxmin()
            return self.data.loc[idx, 'value']
        elif method == 'forward':
            future_data = self.data[self.data['timestamp'] >= query_time]
            if future_data.empty:
                return None
            return future_data.iloc[0]['value']
        elif method == 'backward':
            past_data = self.data[self.data['timestamp'] <= query_time]
            if past_data.empty:
                return None
            return past_data.iloc[-1]['value']
        elif method == 'linear':
            if len(self.data) < 2:
                return self.get_calibration_at_time(timestamp, method='nearest')
            
            # Set timestamp as index for resampling
            temp_data = self.data.set_index('timestamp')
            # Add the query point
            temp_data.loc[query_time] = None
            temp_data = temp_data.sort_index()
            # Interpolate
            temp_data['value'] = temp_data['value'].interpolate(method='linear')
            
            if query_time in temp_data.index:
                return temp_data.loc[query_time, 'value']
            return None
        else:
            raise ValueError(f"Unknown interpolation method: {method}")
    
    def get_all_data(self) -> pd.DataFrame:
        """
        Get all calibration data as a DataFrame.
        
        Returns:
            DataFrame with all calibration points
        """
        return self.data.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Export calibration timeseries to dictionary format.
        
        Returns:
            Dictionary representation of the timeseries
        """
        return {
            'name': self.name,
            'unit': self.unit,
            'data': self.data.to_dict('records')
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeSeriesCalibration':
        """
        Create a timeseries calibration from dictionary format.
        
        Args:
            data: Dictionary containing calibration data
        
        Returns:
            New TimeSeriesCalibration instance
        """
        instance = cls(data['name'], data.get('unit', ''))
        df_data = pd.DataFrame(data['data'])
        if not df_data.empty:
            df_data['timestamp'] = pd.to_datetime(df_data['timestamp'])
            instance.data = df_data
        return instance
