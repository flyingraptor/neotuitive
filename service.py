from datetime import datetime

from cosmos import NearEarthObject
from db.repository import DatabaseOperationError, NeoRiskListDB
from impact import PossibleImpact
from orbit import OrbitProperties

class NeoServiceError(Exception):
    """Base exception for Neo service errors."""


class NeoNotFoundError(NeoServiceError):
    """Raised when the requested NEO is not found in the database."""


class Neo:
    """
    A service class to handle retrieval and composition of Near-Earth Objects (NEOs) 
    from the database, assembling all relevant parts (orbit and impact data).
    """
    
    def __init__(self, db: NeoRiskListDB):
        """
        Initializes the Neo service with a database instance.
        
        :param db: An instance of NeoRiskListDB for database operations.
        """
        self.db = db

    def from_name(self, unique_name: str) -> NearEarthObject:
        """
        Retrieves and constructs a NearEarthObject with all its parts.
        
        :param unique_name: The unique identifier of the NEO.
        :return: A fully composed NearEarthObject.
        :raises NeoNotFoundError: If the NEO is not found in the database.
        :raises DatabaseOperationError: If there is a failure in database operations.
        """
        try:
            # Fetch the main NEO record
            neo_record = self.db.get_neo_by_unique_name(unique_name)
            if not neo_record:
                raise NeoNotFoundError(f"NEO with unique name '{unique_name}' not found.")

            # Fetch orbit properties
            orbit_data = self.db.get_orbit_by_neo_unique_name(unique_name)
            orbit_properties = None
            if orbit_data:
                orbit_properties = OrbitProperties()
                orbit_properties.epoch = orbit_data.epoch_mjd
                orbit_properties.semimajor_axis = orbit_data.semi_major_axis_a
                orbit_properties.eccentricity = orbit_data.eccentricity_e
                orbit_properties.inclination = orbit_data.inclination_i
                orbit_properties.longitude_of_ascending_node = orbit_data.long_of_ascending_node
                orbit_properties.argument_of_perihelion = orbit_data.argument_of_perihelion
                orbit_properties.mean_anomaly = orbit_data.mean_anomaly
                orbit_properties.perihelion_distance = orbit_data.perihelion_distance
                orbit_properties.aphelion_distance = orbit_data.aphelion_distance
                orbit_properties.asc_node_earth_sep = orbit_data.asc_node_earth_sep
                orbit_properties.desc_node_earth_sep = orbit_data.desc_node_earth_sep
                orbit_properties.moid = orbit_data.moid
                orbit_properties.orbital_period = orbit_data.orbital_period
                orbit_properties.u_parameter = orbit_data.u_parameter
                orbit_properties.orbit_type = orbit_data.orbit_type

            # Fetch potential impacts
            impact_records = self.db.get_potential_impacts_by_neo_unique_name(unique_name)
            possible_impacts = [
                PossibleImpact(
                    impact.impact_date_time_utc,
                    impact.ip,
                    impact.expected_energy_mt
                ) for impact in impact_records
            ] if impact_records else []

            # Construct the NearEarthObject
            neo = NearEarthObject(
                name=neo_record.unique_name,
                max_probability_impact_date=neo_record.impact_date_time_utc,
                orbit_properties=orbit_properties,
                possible_impacts=possible_impacts
            )
            
            # Populate additional attributes
            neo.diameter = neo_record.diameter_m
            neo.ip_max = neo_record.ip_max
            neo.ps_max = neo_record.ps_max
            neo.ts = neo_record.ts
            neo.velocity = neo_record.velocity_km_s
            neo.ip_cum = neo_record.ip_cum
            neo.ps_cum = neo_record.ps_cum
            
            return neo

        except DatabaseOperationError as e:
            raise DatabaseOperationError(f"Failed to retrieve NEO '{unique_name}': {e}") from e

    def all(self) -> list[NearEarthObject]:
        """
        Retrieves all NEOs from the database as a list of NearEarthObjects.
        
        :return: List of all NearEarthObjects.
        :raises DatabaseOperationError: If there is a failure in database operations.
        """
        try:
            risky_neos = self.db.get_all_risky_neos()
            return [
                self.from_name(neo.unique_name) for neo in risky_neos
            ]

        except DatabaseOperationError as e:
            raise DatabaseOperationError(f"Failed to retrieve all NEOs: {e}") from e
        
    def by_potential_impact_dates(self, start_date: datetime, end_date: datetime) -> list[NearEarthObject]:
        """
        Retrieves and constructs a list of NearEarthObject instances based on potential impact dates.

        :param start_date: The start date (inclusive, ignoring time).
        :param end_date: The end date (inclusive, ignoring time).
        :return: List of NearEarthObject instances.
        """
        try:
            impact_records = self.db.get_neos_by_impact_dates(start_date, end_date)
            unique_names = set(record.neo_unique_name for record in impact_records)
            return [self.from_name(name) for name in unique_names]
        except DatabaseOperationError as e:
            raise DatabaseOperationError(f"Failed to retrieve NEOs by potential impact dates: {e}") from e