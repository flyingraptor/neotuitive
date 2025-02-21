import unittest
from neotuitive.orbit import OrbitProperties, InvalidValueError

class TestOrbitProperties(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.orbit = OrbitProperties()

    def test_initialization(self):
        """Test that all properties are initialized to None."""
        self.assertIsNone(self.orbit.epoch)
        self.assertIsNone(self.orbit.semimajor_axis)
        self.assertIsNone(self.orbit.eccentricity)
        # ... test other properties

    def test_valid_numeric_properties(self):
        """Test setting valid numeric properties."""
        test_cases = [
            ('epoch', 58849.0),
            ('semimajor_axis', 1.5),
            ('eccentricity', 0.25),
            ('inclination', 15.0),
            ('longitude_of_ascending_node', 180.0),
            ('argument_of_perihelion', 90.0),
            ('mean_anomaly', 45.0),
            ('perihelion_distance', 0.8),
            ('aphelion_distance', 2.2),
            ('asc_node_earth_sep', 0.5),
            ('desc_node_earth_sep', 0.6),
            ('moid', 0.1),
            ('orbital_period', 365.25),
            ('u_parameter', 0.01)
        ]

        for prop_name, value in test_cases:
            setattr(self.orbit, prop_name, value)
            self.assertEqual(getattr(self.orbit, prop_name), value)

    def test_invalid_numeric_properties(self):
        """Test that invalid numeric values raise exceptions."""
        test_cases = [
            ('epoch', 'invalid'),
            ('semimajor_axis', 'invalid'),
            ('eccentricity', 'invalid'),
            # ... add other numeric properties
        ]

        for prop_name, invalid_value in test_cases:
            with self.assertRaises(InvalidValueError):
                setattr(self.orbit, prop_name, invalid_value)

    def test_orbit_type_property(self):
        """Test setting orbit type property."""
        valid_type = "APOLLO"
        self.orbit.orbit_type = valid_type
        self.assertEqual(self.orbit.orbit_type, valid_type)

        with self.assertRaises(InvalidValueError):
            self.orbit.orbit_type = 123  # Invalid type

    def test_string_representation(self):
        """Test string representation of OrbitProperties."""
        self.orbit.epoch = 58849.0
        self.orbit.semimajor_axis = 1.5
        self.orbit.orbit_type = "APOLLO"
        
        str_repr = str(self.orbit)
        self.assertIn("Epoch: 58849.0", str_repr)
        self.assertIn("Semimajor Axis: 1.5", str_repr)
        self.assertIn("Orbit Type: APOLLO", str_repr)

if __name__ == '__main__':
    unittest.main() 