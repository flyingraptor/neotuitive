import unittest
from datetime import datetime
from neotuitive.impact import PossibleImpact, InvalidProbabilityError

class TestPossibleImpact(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.test_date = datetime(2024, 1, 1, 12, 0)
        self.valid_impact = PossibleImpact(
            datetime_utc=self.test_date,
            probability=0.5,
            expected_energy_in_mt=1000.0
        )

    def test_valid_initialization(self):
        """Test valid initialization of PossibleImpact."""
        self.assertEqual(self.valid_impact.datetime_utc, self.test_date)
        self.assertEqual(self.valid_impact.probability, 0.5)
        self.assertEqual(self.valid_impact.expected_energy_in_mt, 1000.0)

    def test_invalid_probability(self):
        """Test that invalid probability values raise an exception."""
        with self.assertRaises(InvalidProbabilityError):
            self.valid_impact.probability = 1.5
        
        with self.assertRaises(InvalidProbabilityError):
            self.valid_impact.probability = -0.1

    def test_string_representation(self):
        """Test the string representation of PossibleImpact."""
        expected_str = f"   Datetime in UTC: {self.test_date} Probability: 0.5 Expected Energy: 1000.0\n"
        self.assertEqual(str(self.valid_impact), expected_str)

    def test_property_setters(self):
        """Test property setters."""
        new_date = datetime(2024, 2, 1, 12, 0)
        self.valid_impact.datetime_utc = new_date
        self.assertEqual(self.valid_impact.datetime_utc, new_date)

        self.valid_impact.probability = 0.75
        self.assertEqual(self.valid_impact.probability, 0.75)

        self.valid_impact.expected_energy_in_mt = 2000.0
        self.assertEqual(self.valid_impact.expected_energy_in_mt, 2000.0)

if __name__ == '__main__':
    unittest.main() 