import unittest
from unittest.mock import Mock, patch
from io import StringIO

from neotuitive.cli import Command
from neotuitive.cosmos import NearEarthObject
from neotuitive.service import Neo

class TestCommand(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.mock_service = Mock(spec=Neo)
        self.command = Command(self.mock_service)
        self.test_neo = Mock(spec=NearEarthObject)
        self.test_neo.name = "2024 TEST"
        self.test_neo.diameter = 100.0
        self.test_neo.velocity = 30.0
        self.test_neo.ip_max = 0.1
        self.test_neo.ps_max = -2.5
        self.test_neo.ts = 1

    @patch('sys.stdout', new_callable=StringIO)
    def test_search_neo_with_results(self, mock_stdout):
        """Test searching NEOs with results."""
        self.mock_service.search.return_value = [self.test_neo]
        
        self.command.search_neo("2024", page=1, page_size=10)
        
        output = mock_stdout.getvalue()
        self.assertIn("2024 TEST", output)
        self.assertIn("100.0 meters", output)
        self.assertIn("30.0 km/s", output)
        self.mock_service.search.assert_called_once_with("2024", 1, 10)

    @patch('sys.stdout', new_callable=StringIO)
    def test_search_neo_no_results(self, mock_stdout):
        """Test searching NEOs with no results."""
        self.mock_service.search.return_value = []
        
        self.command.search_neo("NONEXISTENT")
        
        output = mock_stdout.getvalue()
        self.assertIn("No NEOs found", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_search_neo_error(self, mock_stdout):
        """Test searching NEOs with error."""
        self.mock_service.search.side_effect = Exception("Test error")
        
        self.command.search_neo("2024")
        
        output = mock_stdout.getvalue()
        self.assertIn("Error searching for NEOs", output)
        self.assertIn("Test error", output)

if __name__ == '__main__':
    unittest.main() 