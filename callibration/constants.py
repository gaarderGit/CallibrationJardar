"""
Constants module for storing and managing calibration constants.

This module provides classes for managing calibration constants that are used
in measurement calculations. Constants can be organized by category and version.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json


class CalibrationConstants:
    """
    Manages calibration constants for measurement calculations.
    
    This class provides a structured way to store, retrieve, and version
    calibration constants used in various measurement calculations.
    
    Attributes:
        constants (Dict): Dictionary storing calibration constants
        metadata (Dict): Metadata about the constants including version and date
    """
    
    def __init__(self, version: str = "1.0.0", description: str = ""):
        """
        Initialize calibration constants.
        
        Args:
            version: Version identifier for this set of constants
            description: Description of these calibration constants
        """
        self.constants: Dict[str, Dict[str, Any]] = {}
        self.metadata = {
            'version': version,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'last_modified': datetime.now().isoformat()
        }
    
    def add_constant(self, category: str, name: str, value: Any, 
                    unit: str = "", description: str = "") -> None:
        """
        Add a calibration constant.
        
        Args:
            category: Category grouping for this constant (e.g., 'temperature', 'pressure')
            name: Name of the constant
            value: Value of the constant
            unit: Unit of measurement
            description: Description of what this constant represents
        """
        if category not in self.constants:
            self.constants[category] = {}
        
        self.constants[category][name] = {
            'value': value,
            'unit': unit,
            'description': description,
            'added_at': datetime.now().isoformat()
        }
        self.metadata['last_modified'] = datetime.now().isoformat()
    
    def get_constant(self, category: str, name: str) -> Optional[Any]:
        """
        Get a calibration constant value.
        
        Args:
            category: Category of the constant
            name: Name of the constant
        
        Returns:
            Value of the constant, or None if not found
        """
        if category in self.constants and name in self.constants[category]:
            return self.constants[category][name]['value']
        return None
    
    def get_constant_info(self, category: str, name: str) -> Optional[Dict[str, Any]]:
        """
        Get complete information about a calibration constant.
        
        Args:
            category: Category of the constant
            name: Name of the constant
        
        Returns:
            Dictionary with value, unit, and description, or None if not found
        """
        if category in self.constants and name in self.constants[category]:
            return self.constants[category][name].copy()
        return None
    
    def list_categories(self) -> List[str]:
        """
        List all available constant categories.
        
        Returns:
            List of category names
        """
        return list(self.constants.keys())
    
    def list_constants_in_category(self, category: str) -> List[str]:
        """
        List all constants in a specific category.
        
        Args:
            category: Category to list constants from
        
        Returns:
            List of constant names in the category
        """
        if category in self.constants:
            return list(self.constants[category].keys())
        return []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Export constants to dictionary format.
        
        Returns:
            Dictionary representation of all constants and metadata
        """
        return {
            'metadata': self.metadata,
            'constants': self.constants
        }
    
    def to_json(self, filepath: str) -> None:
        """
        Save constants to a JSON file.
        
        Args:
            filepath: Path to save the JSON file
        """
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CalibrationConstants':
        """
        Create constants from dictionary format.
        
        Args:
            data: Dictionary containing constants and metadata
        
        Returns:
            New CalibrationConstants instance
        """
        metadata = data.get('metadata', {})
        instance = cls(
            version=metadata.get('version', '1.0.0'),
            description=metadata.get('description', '')
        )
        instance.constants = data.get('constants', {})
        instance.metadata = metadata
        return instance
    
    @classmethod
    def from_json(cls, filepath: str) -> 'CalibrationConstants':
        """
        Load constants from a JSON file.
        
        Args:
            filepath: Path to the JSON file
        
        Returns:
            New CalibrationConstants instance
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
