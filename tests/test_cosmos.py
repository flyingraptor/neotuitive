import unittest
from datetime import datetime
from unittest.mock import Mock

from cosmos import (
    NearEarthObject, _SpaceObject, InvalidDiameterError, 
    InvalidVelocityError, InvalidProbabilityError
)
from impact import PossibleImpact
from orbit import OrbitProperties

class TestSpaceObject(unittest.TestCase):
    def test_initialization(self):
        """Test basic initialization of _SpaceObject."""
        obj = _SpaceObject("Test Object")
        self.assertEqual(obj.name, "Test Object")
        
    def test_invalid_name(self):
        """Test setting invalid name type."""
        obj = _SpaceObject("Test")
        with self.assertRaises(TypeError):
            obj.name = 123
            
    def test_string_representation(self):
        """Test string representation of _SpaceObject."""
        obj = _SpaceObject("Test Object")
        self.assertEqual(str(obj), "Name: Test Object")

class TestNearEarthObject(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.test_date = datetime(2024, 1, 1)
        self.orbit_props = Mock(spec=OrbitProperties)
        self.possible_impact = Mock(spec=PossibleImpact)
        
        self.neo = NearEarthObject(
            name="2024 TEST",
            max_probability_impact_date=self.test_date,
            orbit_properties=self.orbit_props,
            possible_impacts=[self.possible_impact]
        )

    def test_valid_initialization(self):
        """Test valid initialization of NearEarthObject."""
        self.assertEqual(self.neo.name, "2024 TEST")
        self.assertEqual(self.neo._max_probability_impact_date, self.test_date)
        self.assertEqual(self.neo.orbit_properties, self.orbit_props)
        self.assertEqual(self.neo.possible_impacts, [self.possible_impact])

    def test_invalid_initialization(self):
        """Test initialization with invalid date type."""
        with self.assertRaises(TypeError):
            NearEarthObject(
                name="Test",
                max_probability_impact_date="invalid date",
                orbit_properties=self.orbit_props
            )

    def test_diameter_property(self):
        """Test diameter property setter and getter."""
        self.neo.diameter = 100.0
        self.assertEqual(self.neo.diameter, 100.0)

        with self.assertRaises(InvalidDiameterError):
            self.neo.diameter = -1.0
            
        with self.assertRaises(TypeError):
            self.neo.diameter = "invalid"

    def test_velocity_property(self):
        """Test velocity property setter and getter."""
        self.neo.velocity = 30.0
        self.assertEqual(self.neo.velocity, 30.0)

        with self.assertRaises(InvalidVelocityError):
            self.neo.velocity = -1.0
            
        with self.assertRaises(TypeError):
            self.neo.velocity = "invalid"

    def test_probability_properties(self):
        """Test probability-related properties."""
        valid_probabilities = [0.00000, 0.0005, 1.0, 0.9999999, 0.3]
        invalid_probabilities = [-0.133, 1.1]

        # Test ip_max
        for prob in valid_probabilities:
            self.neo.ip_max = prob
            self.assertEqual(self.neo.ip_max, prob)

        for prob in invalid_probabilities:
            with self.assertRaises(InvalidProbabilityError):
                self.neo.ip_max = prob

        # Test ip_cum
        for prob in valid_probabilities:
            self.neo.ip_cum = prob
            self.assertEqual(self.neo.ip_cum, prob)

        for prob in invalid_probabilities:
            with self.assertRaises(InvalidProbabilityError):
                self.neo.ip_cum = prob

    def test_scale_properties(self):
        """Test Palermo and Torino scale properties."""
        # Test ps_max
        self.neo.ps_max = -2.5
        self.assertEqual(self.neo.ps_max, -2.5)
        
        # Test ps_cum
        self.neo.ps_cum = -1.8
        self.assertEqual(self.neo.ps_cum, -1.8)
        
        # Test ts
        self.neo.ts = 1
        self.assertEqual(self.neo.ts, 1)

    def test_days_in_list_property(self):
        """Test days_in_list property."""
        self.neo.days_in_list = 30
        self.assertEqual(self.neo.days_in_list, 30)

        with self.assertRaises(TypeError):
            self.neo.days_in_list = "invalid"

    def test_orbit_properties_setter(self):
        """Test orbit_properties setter validation."""
        new_orbit = Mock(spec=OrbitProperties)
        self.neo.orbit_properties = new_orbit
        self.assertEqual(self.neo.orbit_properties, new_orbit)

        with self.assertRaises(TypeError):
            self.neo.orbit_properties = "invalid"

    def test_possible_impacts_setter(self):
        """Test possible_impacts setter validation."""
        new_impact = Mock(spec=PossibleImpact)
        self.neo.possible_impacts = [new_impact]
        self.assertEqual(self.neo.possible_impacts, [new_impact])

        with self.assertRaises(TypeError):
            self.neo.possible_impacts = [123]  # Invalid impact object
            
        with self.assertRaises(TypeError):
            self.neo.possible_impacts = "invalid"  # Not a list

    def test_string_representation(self):
        """Test string representation of NearEarthObject."""
        self.neo.diameter = 100.0
        str_repr = str(self.neo)
        
        self.assertIn("2024 TEST", str_repr)
        self.assertIn("100.0 meters", str_repr)
        self.assertIn(self.test_date.strftime("%Y-%m-%d"), str_repr)

if __name__ == '__main__':
    unittest.main() 