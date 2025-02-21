from datetime import datetime

from impact import PossibleImpact
from orbit import OrbitProperties

class NearEarthObjectError(Exception):
    """Base exception for errors related to NearEarthObject."""

class InvalidDiameterError(NearEarthObjectError):
    """Exception raised when an invalid diameter is set."""

class InvalidVelocityError(NearEarthObjectError):
    """Exception raised when an invalid velocity is set."""

class InvalidProbabilityError(NearEarthObjectError):
    """Exception raised when an invalid probability value is set."""

class _SpaceObject:
    """Base class representing a generic space object."""
    
    def __init__(self, name: str):
        """
        Initialize a space object with a name.

        :param name: Name of the space object.
        """
        self._name = name

    def __str__(self):
        """Return a string representation of the space object."""
        return f"Name: {self._name}"
    
    @property
    def name(self):
        """Get the name of the space object."""
        return self._name
    
    @name.setter
    def name(self, name: str):
        """Set the name of the space object."""
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        self._name = name
        return self


class NearEarthObject(_SpaceObject):
    """Class representing a Near-Earth Object (NEO) with its properties and risk factors."""
    
    def __init__(self, name: str, 
                 max_probability_impact_date: datetime,
                 orbit_properties: OrbitProperties,
                 possible_impacts: list[PossibleImpact] = None):
        """
        Initialize a Near-Earth Object with orbital properties, close approaches, and possible impacts.

        :param name: Name of the NEO.
        :param max_probability_impact_date: Date of the maximum probability of impact.
        :param orbit_properties: Orbital properties of the NEO.
        :param possible_impacts: List of possible impacts.
        """
        super().__init__(name)
        
        self._orbit_properties = orbit_properties or None
        self._possible_impacts = possible_impacts or []

        # Additional properties
        if not isinstance(max_probability_impact_date, datetime):
            raise TypeError("max_probability_impact_date must be a datetime object.")
        self._max_probability_impact_date = max_probability_impact_date
        self._diameter_in_m = None
        self._ip_max = None
        self._ps_max = None
        self._ts = None
        self._velocity = None
        self._ip_cum = None
        self._ps_cum = None
        self._days_in_list = None

    def __str__(self):
        """Return a detailed string representation of the Near-Earth Object."""
        return (
            f"\nNEO {super().__str__()} \n"
            f"Max Probability Impact Date: {self._max_probability_impact_date}\n"
            f"Diameter: {self._diameter_in_m} meters\n"
            f"Orbit Properties:\n{self._orbit_properties}\n"
            f"Possible Impacts:\n{''.join(map(str, self._possible_impacts))}\n"
        )
    
    @property
    def diameter(self):
        """Get the diameter of the NEO in meters."""
        return self._diameter_in_m

    @diameter.setter
    def diameter(self, diameter: float):
        """Set the diameter of the NEO in meters."""
        if not isinstance(diameter, (float, int)):
            raise TypeError("Diameter must be a number.")
        if diameter <= 0:
            raise InvalidDiameterError("Diameter must be a positive number.")
        self._diameter_in_m = diameter
        return self

    @property
    def ip_max(self):
        """Get the maximum impact probability."""
        return self._ip_max
    
    @ip_max.setter
    def ip_max(self, ip_max: float):
        """Set the maximum impact probability."""
        if not isinstance(ip_max, (float, int)):
            raise TypeError("Impact probability must be a number.")
        if not (0 <= ip_max <= 1):
            raise InvalidProbabilityError("Impact probability must be between 0 and 1 (0% - 100%).")
        self._ip_max = ip_max
        return self

    @property
    def ps_max(self):
        """Get the maximum Palermo Scale value."""
        return self._ps_max
    
    @ps_max.setter
    def ps_max(self, ps_max: float):
        """Set the maximum Palermo Scale value."""
        if not isinstance(ps_max, (float, int)):
            raise TypeError("Palermo Scale value must be a number.")
        self._ps_max = ps_max
        return self

    @property
    def ts(self):
        """Get the Torino Scale value."""
        return self._ts
    
    @ts.setter
    def ts(self, ts: int):
        """Set the Torino Scale value."""
        if not isinstance(ts, (float, int)):
            raise TypeError("Torino Scale value must be an number.")
        self._ts = ts
        return self

    @property
    def ip_cum(self):
        """Get the cumulative impact probability."""
        return self._ip_cum
    
    @ip_cum.setter
    def ip_cum(self, ip_cum: float):
        """Set the cumulative impact probability."""
        if not isinstance(ip_cum, (float, int)):
            raise TypeError("Cumulative impact probability must be a number.")
        if not (0 <= ip_cum <= 1):
            raise InvalidProbabilityError("Impact probability must be between 0 and 1 (0% - 100%).")
        self._ip_cum = ip_cum
        return self

    @property
    def ps_cum(self):
        """Get the cumulative Palermo Scale value."""
        return self._ps_cum
    
    @ps_cum.setter    
    def ps_cum(self, ps_cum: float):
        """Set the cumulative Palermo Scale value."""
        if not isinstance(ps_cum, (float, int)):
            raise TypeError("Cumulative Palermo Scale value must be a number.")
        self._ps_cum = ps_cum
        return self

    @property
    def velocity(self):
        """Get the velocity of the NEO in km/s."""
        return self._velocity
    
    @velocity.setter
    def velocity(self, velocity: float):
        """Set the velocity of the NEO in km/s."""
        if not isinstance(velocity, (float, int)):
            raise TypeError("Velocity must be a number.")
        if velocity <= 0:
            raise InvalidVelocityError("Velocity must be a positive number.")
        self._velocity = velocity
        return self

    @property
    def days_in_list(self):
        """Get the number of days the NEO has been listed."""
        return self._days_in_list
    
    @days_in_list.setter
    def days_in_list(self, days: int):
        """Set the number of days the NEO has been listed."""
        if not isinstance(days, int):
            raise TypeError("Days in list must be an integer.")
        self._days_in_list = days
        return self

    @property
    def orbit_properties(self) -> OrbitProperties:
        """Get the orbit properties of the NEO."""
        return self._orbit_properties
    
    @orbit_properties.setter
    def orbit_properties(self, orbit_properties: OrbitProperties):
        """Set the orbit properties of the NEO."""
        if not isinstance(orbit_properties, OrbitProperties):
            raise TypeError("Orbit properties must be an instance of OrbitProperties.")
        self._orbit_properties = orbit_properties
        return self

    @property
    def possible_impacts(self):
        """Get the list of possible impacts."""
        return self._possible_impacts
    
    @possible_impacts.setter
    def possible_impacts(self, possible_impacts: list[PossibleImpact]):
        """Set the list of possible impacts."""
        if not isinstance(possible_impacts, list):
            raise TypeError("Possible impacts must be provided as a list.")
        if not all(isinstance(pi, PossibleImpact) for pi in possible_impacts):
            raise TypeError("All items in possible impacts must be instances of PossibleImpact.")
        self._possible_impacts = possible_impacts
        return self