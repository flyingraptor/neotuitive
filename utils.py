from astropy import units as u
from astropy.time import Time
from poliastro.bodies import Earth, Sun
from poliastro.ephem import Ephem
from poliastro.frames import Planes
from poliastro.twobody import Orbit
from poliastro.twobody.angles import E_to_nu, M_to_E

def create_orbit(neo_obj, epoch): 
    """
    Create a poliastro Orbit object from a Near-Earth Object (NEO).
    """
    orbit_properties = neo_obj.orbit_properties
    if not orbit_properties:
        return None  # Skip if no orbit data is available
    
    try:
        # Extract orbital elements
        a = orbit_properties.semimajor_axis << u.AU
        ecc = orbit_properties.eccentricity << u.one
        inc = orbit_properties.inclination << u.deg
        raan = orbit_properties.longitude_of_ascending_node << u.deg
        argp = orbit_properties.argument_of_perihelion << u.deg
        mean_anomaly = orbit_properties.mean_anomaly << u.deg
        
        # Compute true anomaly
        nu = E_to_nu(M_to_E(mean_anomaly, ecc), ecc)

        # Create an orbit object
        return Orbit.from_classical(
            Sun, a, ecc, inc, raan, argp, nu, epoch, 
            plane=Planes.EARTH_ECLIPTIC
        )
        
    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error creating poliastro orbit {neo_obj.name}: {e}")
        return None

def compute_neo_position(neo_obj, epoch):
    """
    Compute the 3D position (x, y, z) of a Near-Earth Object (NEO).
    """
    try:
        # Create an orbit object
        neo_orbit = create_orbit(neo_obj, epoch)

        if neo_orbit is None:
            return None

        # Extract position in 3D (x, y, z)
        x, y, z = neo_orbit.r.to_value(u.km)  # Convert to km

        return x, y, z  # Return full 3D coordinates
    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error computing NEO position {neo_obj.name}: {e}")
        return None

def compute_earth_position(epoch: Time):
    """
    Compute the 3D position (x, y, z) of Earth in the heliocentric frame 
    at a given epoch.
    """
    try:
        # Create an Ephem object for Earth
        earth_ephem = Ephem.from_body(Earth, epoch)

        # Get position vector in the heliocentric frame
        r_heliocentric = earth_ephem.rv(epoch)[0]  # Extract position vector

        # Convert to kilometers
        x_earth, y_earth, z_earth = r_heliocentric.to_value(u.km)

        return x_earth, y_earth, z_earth
    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error computing Earth's position: {e}")
        return None
