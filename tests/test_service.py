import unittest
from datetime import datetime
from unittest.mock import Mock

from neotuitive.db.repository import NeoRiskListDB, RiskyNEO, NEOOrbit, NEOPotentialImpact
from neotuitive.service import Neo, NeoNotFoundError, DatabaseOperationError

class TestNeoService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db = Mock(spec=NeoRiskListDB)
        self.service = Neo(self.mock_db)
        
        # Setup common test data
        self.test_date = datetime(2024, 1, 1)
        self.test_neo_name = "2024 TEST"
        
        # Mock RiskyNEO record
        self.mock_risky_neo = Mock(spec=RiskyNEO)
        self.mock_risky_neo.unique_name = self.test_neo_name
        self.mock_risky_neo.diameter_m = 100.0
        self.mock_risky_neo.impact_date_time_utc = self.test_date
        self.mock_risky_neo.ip_max = 0.1
        self.mock_risky_neo.ps_max = -2.5
        self.mock_risky_neo.ts = 1
        self.mock_risky_neo.velocity_km_s = 30.0
        self.mock_risky_neo.ip_cum = 0.15
        self.mock_risky_neo.ps_cum = -2.0
        
        # Mock NEOOrbit record
        self.mock_orbit = Mock(spec=NEOOrbit)
        self.mock_orbit.epoch_mjd = 58849.0
        self.mock_orbit.epoch_as_date = self.test_date
        self.mock_orbit.parameters_type = "COMET"
        self.mock_orbit.neo_unique_name = self.test_neo_name
        self.mock_orbit.inclination_i = 15.0
        self.mock_orbit.long_of_ascending_node = 180.0
        self.mock_orbit.argument_of_perihelion = 90.0
        self.mock_orbit.mean_anomaly = 45.0
        self.mock_orbit.perihelion_distance = 1.0
        self.mock_orbit.aphelion_distance = 2.0
        self.mock_orbit.asc_node_earth_sep = 1.0
        self.mock_orbit.desc_node_earth_sep = 2.0
        self.mock_orbit.semi_major_axis_a = 1.5
        self.mock_orbit.eccentricity_e = 0.25
        self.mock_orbit.orbit_type = "APOLLO"
        self.mock_orbit.record_id = "1234567890"
        self.mock_orbit.u_parameter = 0.1
        self.mock_orbit.orbital_period = 1.0
        self.mock_orbit.moid = 0.1
        
        # Mock NEOPotentialImpact records
        self.mock_impact = Mock(spec=NEOPotentialImpact)
        self.mock_impact.impact_date_time_utc = self.test_date
        self.mock_impact.record_id = "1234567890"
        self.mock_impact.sigma = 0.1
        self.mock_impact.sigma_imp = 0.1
        self.mock_impact.dis_plus_minus_w_re = 0.1
        self.mock_impact.stretch = 0.1
        self.mock_impact.ip = 0.1
        self.mock_impact.expected_energy_mt = 1000.0
        self.mock_impact.ps = 0.1
        self.mock_impact.ts = 0.1
        self.mock_impact.neo_unique_name = self.test_neo_name
        self.mock_impact.mjd = 58849.0
        

    def test_from_name_success(self):
        """Test successful retrieval of NEO by name."""
        # Setup mock returns
        self.mock_db.get_neo_by_unique_name.return_value = self.mock_risky_neo
        self.mock_db.get_orbit_by_neo_unique_name.return_value = self.mock_orbit
        self.mock_db.get_potential_impacts_by_neo_unique_name.return_value = [self.mock_impact]
        
        # Execute test
        neo = self.service.from_name(self.test_neo_name)
        
        # Verify results
        self.assertEqual(neo.name, self.test_neo_name)
        self.assertEqual(neo.diameter, 100.0)
        self.assertEqual(neo.velocity, 30.0)
        self.assertEqual(neo.ip_max, 0.1)
        self.assertEqual(neo.ps_max, -2.5)
        self.assertEqual(neo.ts, 1)
        
        # Verify orbit properties were set
        self.assertIsNotNone(neo.orbit_properties)
        self.assertEqual(neo.orbit_properties.orbit_type, "APOLLO")
        
        # Verify possible impacts were set
        self.assertEqual(len(neo.possible_impacts), 1)
        self.assertEqual(neo.possible_impacts[0].probability, 0.1)

    def test_from_name_not_found(self):
        """Test NEO not found case."""
        self.mock_db.get_neo_by_unique_name.return_value = None
        
        with self.assertRaises(NeoNotFoundError):
            self.service.from_name("NONEXISTENT")

    def test_from_name_database_error(self):
        """Test database error handling."""
        self.mock_db.get_neo_by_unique_name.side_effect = DatabaseOperationError("DB Error")
        
        with self.assertRaises(DatabaseOperationError):
            self.service.from_name(self.test_neo_name)

    def test_all_empty(self):
        """Test case when no NEOs exist."""
        self.mock_db.get_all_risky_neos.return_value = []
        
        neos = self.service.all()
        self.assertEqual(len(neos), 0)

    def test_by_potential_impact_dates(self):
        """Test retrieval of NEOs by impact date range."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        # Setup mock returns
        self.mock_db.get_neos_by_impact_dates.return_value = [self.mock_impact]
        self.mock_db.get_neo_by_unique_name.return_value = self.mock_risky_neo
        self.mock_db.get_orbit_by_neo_unique_name.return_value = self.mock_orbit
        self.mock_db.get_potential_impacts_by_neo_unique_name.return_value = [self.mock_impact]
        
        # Execute test
        neos = self.service.by_potential_impact_dates(start_date, end_date)
        
        # Verify results
        self.assertEqual(len(neos), 1)
        self.assertEqual(neos[0].name, self.test_neo_name)
        
        # Verify the database was called with correct parameters
        self.mock_db.get_neos_by_impact_dates.assert_called_once_with(start_date, end_date)

    def test_by_potential_impact_dates_database_error(self):
        """Test database error handling in impact dates retrieval."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        self.mock_db.get_neos_by_impact_dates.side_effect = DatabaseOperationError("DB Error")
        
        with self.assertRaises(DatabaseOperationError):
            self.service.by_potential_impact_dates(start_date, end_date)

if __name__ == '__main__':
    unittest.main() 