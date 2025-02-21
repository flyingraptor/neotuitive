class OrbitPropertiesError(Exception):
    """Base class for exceptions in this module."""

class InvalidValueError(OrbitPropertiesError):
    """Exception raised for errors in the input value."""
    def __init__(self, property_name, message="Invalid value provided"):
        self.property_name = property_name
        self.message = message
        super().__init__(f"{self.property_name}: {self.message}")

class OrbitProperties:
    """ 
    A class to represent the properties of an orbit. 
    
    Attributes
    ----------
    epoch : float
        Modified Julian Date (MJD) representing the epoch of the orbital elements.
    semimajor_axis : float
        The semi-major axis of the orbit in Astronomical Units (AU). 
        This parameter defines the size of the orbit.
    eccentricity : float
        The eccentricity of the orbit (dimensionless). 
        This parameter defines the shape of the orbit.
    inclination : float
        The inclination of the orbit with respect to the ecliptic plane in degrees.
        This parameter defines the inclination of the asteroid orbital plane with respect 
        to the horizontal plane of reference of the J2000 ecliptic reference frame.
    longitude_of_ascending_node : float
        The longitude of the ascending node in degrees. This angle identifies the point
        at which the asteroid crosses the horizontal reference plane in ascending direction.
    argument_of_perihelion : float
        The argument of perihelion in degrees. 
    mean_anomaly : float
        The mean anomaly at the epoch in degrees.
    perihelion_distance : float
        The distance from the Sun at perihelion in AU. 
        This parameter defines the maximum distance from the Sun in AU along the osculating ellipse.  
    aphelion_distance : float
        This parameter defines the minimum distance from the Sun in AU along the osculating ellipse.
    asc_node_earth_sep : float
        The minimum separation between Earth's orbit and the ascending node in AU.
    desc_node_earth_sep : float
        The minimum separation between Earth's orbit and the descending node in AU.
    moid : float
        Minimum Orbit Intersection Distance with Earth's orbit in AU.
    orbital_period : float
        The orbital period in years.
    u_parameter : float
        U parameter for orbit uncertainty estimation.
    orbit_type : str
        Classification of the orbit type.
    """
    
    def __init__(self):
        """ Initialize all properties to None. """
        self._epoch = None
        self._semimajor_axis = None
        self._eccentricity = None
        self._inclination = None
        self._longitude_of_ascending_node = None
        self._argument_of_perihelion = None
        self._mean_anomaly = None
        self._perihelion_distance = None
        self._aphelion_distance = None
        self._asc_node_earth_sep = None
        self._desc_node_earth_sep = None
        self._moid = None
        self._orbital_period = None
        self._u_parameter = None
        self._orbit_type = None

    def __str__(self):
        """
        Return a string representation of the object.
        Returns:
            str: A string representation of the orbit properties with non-None values.
        """
        return f"   Epoch: {self.epoch}\n" \
               f"   Semimajor Axis: {self.semimajor_axis}\n" \
               f"   Eccentricity: {self.eccentricity}\n" \
               f"   Inclination: {self.inclination}\n" \
               f"   Longitude of Ascending Node: {self.longitude_of_ascending_node}\n" \
               f"   Argument of Perihelion: {self.argument_of_perihelion}\n" \
               f"   Mean Anomaly: {self.mean_anomaly}\n" \
               f"   Perihelion Distance: {self.perihelion_distance}\n" \
               f"   Aphelion Distance: {self.aphelion_distance}\n" \
               f"   Ascending Node Earth Separation: {self.asc_node_earth_sep}\n" \
               f"   Descending Node Earth Separation: {self.desc_node_earth_sep}\n" \
               f"   MOID: {self.moid}\n" \
               f"   Orbital Period: {self.orbital_period}\n" \
               f"   U Parameter: {self.u_parameter}\n" \
               f"   Orbit Type: {self.orbit_type}"
    
    @property
    def epoch(self):
        """Get the epoch property."""
        return self._epoch
    
    @epoch.setter
    def epoch(self, epoch):
        """Set the epoch property."""
        if not isinstance(epoch, (int, float)):
            raise InvalidValueError("epoch", "Epoch must be a number")
        self._epoch = epoch

    @property
    def semimajor_axis(self):
        """Get the semimajor_axis property."""
        return self._semimajor_axis
    
    @semimajor_axis.setter
    def semimajor_axis(self, semimajor_axis):
        """Set the semimajor_axis property."""
        if not isinstance(semimajor_axis, (int, float)):
            raise InvalidValueError("semimajor_axis", "Semimajor axis must be a number")
        self._semimajor_axis = semimajor_axis
        return self

    @property
    def eccentricity(self):
        """Get the eccentricity property."""
        return self._eccentricity
    
    @eccentricity.setter
    def eccentricity(self, eccentricity):
        """Set the eccentricity property."""
        if not isinstance(eccentricity, (int, float)):
            raise InvalidValueError("eccentricity", "Eccentricity must be a number")
        self._eccentricity = eccentricity
        return self

    @property
    def inclination(self):
        """Get the inclination property."""
        return self._inclination
    
    @inclination.setter
    def inclination(self, inclination):
        """Set the inclination property."""
        if not isinstance(inclination, (int, float)):
            raise InvalidValueError("inclination", "Inclination must be a number")
        self._inclination = inclination
        return self

    @property
    def longitude_of_ascending_node(self):
        """Get the longitude_of_ascending_node property."""
        return self._longitude_of_ascending_node
    
    @longitude_of_ascending_node.setter
    def longitude_of_ascending_node(self, longitude_of_ascending_node):
        """Set the longitude_of_ascending_node property."""
        if not isinstance(longitude_of_ascending_node, (int, float)):
            raise InvalidValueError("longitude_of_ascending_node", "Longitude of ascending node must be a number")
        self._longitude_of_ascending_node = longitude_of_ascending_node
        return self

    @property
    def argument_of_perihelion(self):
        """Get the argument_of_perihelion property."""
        return self._argument_of_perihelion
    
    @argument_of_perihelion.setter
    def argument_of_perihelion(self, argument_of_perihelion):
        """Set the argument_of_perihelion property."""
        if not isinstance(argument_of_perihelion, (int, float)):
            raise InvalidValueError("argument_of_perihelion", "Argument of perihelion must be a number")
        self._argument_of_perihelion = argument_of_perihelion
        return self

    @property
    def mean_anomaly(self):
        """Get the mean_anomaly property."""
        return self._mean_anomaly
    
    @mean_anomaly.setter
    def mean_anomaly(self, mean_anomaly):
        """Set the mean_anomaly property."""
        if not isinstance(mean_anomaly, (int, float)):
            raise InvalidValueError("mean_anomaly", "Mean anomaly must be a number")
        self._mean_anomaly = mean_anomaly
        return self

    @property
    def perihelion_distance(self):
        """Get the perihelion_distance property."""
        return self._perihelion_distance
    
    @perihelion_distance.setter
    def perihelion_distance(self, perihelion_distance):
        """Set the perihelion_distance property."""
        if not isinstance(perihelion_distance, (int, float)):
            raise InvalidValueError("perihelion_distance", "Perihelion distance must be a number")
        self._perihelion_distance = perihelion_distance
        return self

    @property
    def aphelion_distance(self):
        """Get the aphelion_distance property."""
        return self._aphelion_distance
    
    @aphelion_distance.setter
    def aphelion_distance(self, aphelion_distance):
        """Set the aphelion_distance property."""
        if not isinstance(aphelion_distance, (int, float)):
            raise InvalidValueError("aphelion_distance", "Aphelion distance must be a number")
        self._aphelion_distance = aphelion_distance
        return self

    @property
    def asc_node_earth_sep(self):
        """Get the asc_node_earth_sep property."""
        return self._asc_node_earth_sep
    
    @asc_node_earth_sep.setter
    def asc_node_earth_sep(self, asc_node_earth_sep):
        """Set the asc_node_earth_sep property."""
        if not isinstance(asc_node_earth_sep, (int, float)):
            raise InvalidValueError("asc_node_earth_sep", "Ascending node Earth separation must be a number")
        self._asc_node_earth_sep = asc_node_earth_sep
        return self

    @property
    def desc_node_earth_sep(self):
        """Get the desc_node_earth_sep property."""
        return self._desc_node_earth_sep
    
    @desc_node_earth_sep.setter
    def desc_node_earth_sep(self, desc_node_earth_sep):
        """Set the desc_node_earth_sep property."""
        if not isinstance(desc_node_earth_sep, (int, float)):
            raise InvalidValueError("desc_node_earth_sep", "Descending node Earth separation must be a number")
        self._desc_node_earth_sep = desc_node_earth_sep
        return self

    @property
    def moid(self):
        """Get the moid property."""
        return self._moid
    
    @moid.setter
    def moid(self, moid):
        """Set the moid property."""
        if not isinstance(moid, (int, float)):
            raise InvalidValueError("moid", "MOID must be a number")
        self._moid = moid
        return self

    @property
    def orbital_period(self):
        """Get the orbital_period property."""
        return self._orbital_period
    
    @orbital_period.setter
    def orbital_period(self, orbital_period):
        """Set the orbital_period property."""
        if not isinstance(orbital_period, (int, float)):
            raise InvalidValueError("orbital_period", "Orbital period must be a number")
        self._orbital_period = orbital_period
        return self

    @property
    def u_parameter(self):
        """Get the u_parameter property."""
        return self._u_parameter
    
    @u_parameter.setter
    def u_parameter(self, u_parameter):
        """Set the u_parameter property."""
        if not isinstance(u_parameter, (int, float)):
            raise InvalidValueError("u_parameter", "U parameter must be a number")
        self._u_parameter = u_parameter
        return self

    @property
    def orbit_type(self):
        """Get the orbit_type property."""
        return self._orbit_type
    
    @orbit_type.setter
    def orbit_type(self, orbit_type):
        """Set the orbit_type property."""
        if not isinstance(orbit_type, str):
            raise InvalidValueError("orbit_type", "Orbit type must be a string")
        self._orbit_type = orbit_type
        return self
    