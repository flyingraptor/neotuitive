from datetime import datetime
import sqlite3
import sys
from typing import List
import uuid


class NeoRiskListDBError(Exception):
    """Base exception for NeoRiskListDB errors."""


class DatabaseConnectionError(NeoRiskListDBError):
    """Exception raised for database connection errors."""

class DatabaseOperationError(NeoRiskListDBError):
    """Exception raised for database operation failures."""

class RiskyNEO:
    """Data Transfer Object (DTO) of Near-Earth Object (NEO) with potential impact risk."""

    def __init__(self, unique_name: str, diameter_m: float, impact_date_time_utc: datetime,
                 ip_max: float, ps_max: float, ts: float, velocity_km_s: float,
                 years: str, ip_cum: float, ps_cum: float):
        self.unique_name = unique_name
        self.diameter_m = diameter_m
        self.impact_date_time_utc = impact_date_time_utc
        self.ip_max = ip_max
        self.ps_max = ps_max
        self.ts = ts
        self.velocity_km_s = velocity_km_s
        self.years = years
        self.ip_cum = ip_cum
        self.ps_cum = ps_cum

    def as_list(self) -> List:
        """Returns the object's attributes as a list."""
        return [
            self.unique_name, self.diameter_m, self.impact_date_time_utc,
            self.ip_max, self.ps_max, self.ts, self.velocity_km_s,
            self.years, self.ip_cum, self.ps_cum
        ]


class NEOOrbit:
    """Data Transfer Object (DTO) for Near-Earth Object (NEO) orbit properties."""

    def __init__(self, parameters_type: str, neo_unique_name: str, epoch_mjd: float, epoch_as_date: datetime,
                 semi_major_axis_a: float, eccentricity_e: float, inclination_i: float,
                 long_of_ascending_node: float, argument_of_perihelion: float, mean_anomaly: float,
                 perihelion_distance: float, aphelion_distance: float, asc_node_earth_sep: float,
                 desc_node_earth_sep: float, moid: float, orbital_period: float,
                 u_parameter: float, orbit_type: str, record_id: str = None):
        self.record_id = record_id or str(uuid.uuid4())
        self.parameters_type = parameters_type
        self.neo_unique_name = neo_unique_name
        self.epoch_mjd = epoch_mjd
        self.epoch_as_date = epoch_as_date
        self.semi_major_axis_a = semi_major_axis_a
        self.eccentricity_e = eccentricity_e
        self.inclination_i = inclination_i
        self.long_of_ascending_node = long_of_ascending_node
        self.argument_of_perihelion = argument_of_perihelion
        self.mean_anomaly = mean_anomaly
        self.perihelion_distance = perihelion_distance
        self.aphelion_distance = aphelion_distance
        self.asc_node_earth_sep = asc_node_earth_sep
        self.desc_node_earth_sep = desc_node_earth_sep
        self.moid = moid
        self.orbital_period = orbital_period
        self.u_parameter = u_parameter
        self.orbit_type = orbit_type

    def as_list(self) -> List:
        """Return the NEO orbit properties as a list."""
        return [
            self.record_id,
            self.parameters_type,
            self.neo_unique_name,
            self.epoch_mjd,
            self.epoch_as_date,
            self.semi_major_axis_a,
            self.eccentricity_e,
            self.inclination_i,
            self.long_of_ascending_node,
            self.argument_of_perihelion,
            self.mean_anomaly,
            self.perihelion_distance,
            self.aphelion_distance,
            self.asc_node_earth_sep,
            self.desc_node_earth_sep,
            self.moid,
            self.orbital_period,
            self.u_parameter,
            self.orbit_type
        ]


class NEOPotentialImpact:
    """Data Transfer Object (DTO) for Near-Earth Object (NEO) potential impact data."""

    def __init__(self, neo_unique_name: str, impact_date_time_utc: datetime, mjd: float,
                 sigma: float, sigma_imp: float, dis_plus_minus_w_re: float, stretch: float,
                 ip: float, expected_energy_mt: float, ps: float, ts: float, record_id: str = None):
        """Initialize an NEOPotentialImpact DTO with impact properties."""
        self.record_id = record_id or str(uuid.uuid4())
        self.neo_unique_name = neo_unique_name
        self.impact_date_time_utc = impact_date_time_utc
        self.mjd = mjd
        self.sigma = sigma
        self.sigma_imp = sigma_imp
        self.dis_plus_minus_w_re = dis_plus_minus_w_re
        self.stretch = stretch
        self.ip = ip
        self.expected_energy_mt = expected_energy_mt
        self.ps = ps
        self.ts = ts

    def as_list(self) -> List:
        """Returns the object's attributes as a list."""
        return [
            self.record_id,
            self.neo_unique_name,
            self.impact_date_time_utc,
            self.mjd,
            self.sigma,
            self.sigma_imp,
            self.dis_plus_minus_w_re,
            self.stretch,
            self.ip,
            self.expected_energy_mt,
            self.ps,
            self.ts
        ]

    def __str__(self):
        """String representation of the NEOPotentialImpact object."""
        return f"NEOPotentialImpact({self.neo_unique_name}, Impact UTC: {self.impact_date_time_utc}, IP: {self.ip})"


class NeoRiskListDB:
    """Handles database operations for Near-Earth Object (NEO) risk list."""

    def __init__(self, db_name: str = "near_earth_objects.db"):
        """Initialize the database connection and create the necessary table."""
        self.db_name = db_name
        try:
            self.conn = sqlite3.connect(
                self.db_name, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            self.cursor = self.conn.cursor()
            self._create_risky_neo_table()
            self._create_risky_neo_orbits_table()
            self._create_risky_neo_potential_impacts_table()
            self._close_connection()
        except sqlite3.Error as e:
            raise DatabaseConnectionError(
                f"Failed to connect to the database: {e}")

    def store_risky_neo_orbits(self, orbit_dtos: List[NEOOrbit]):
        """
        Inserts multiple NEO orbit records into the risky_neo_orbits table in a batch.

        :param orbit_dtos: List of NEOOrbit DTOs to insert.
        :raises DatabaseOperationError: If insertion fails.
        """
        try:
            if not isinstance(orbit_dtos, list) or not all(isinstance(dto, NEOOrbit) for dto in orbit_dtos):
                raise TypeError("Expected a list of NEOOrbit DTOs.")

            # Convert DTOs to a list of tuples for batch insertion
            data_tuples = [dto.as_list() for dto in orbit_dtos]

            # Connect to db
            self.conn = sqlite3.connect(
                self.db_name, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            self.cursor = self.conn.cursor()

            # Execute batch insert
            self.cursor.executemany('''
                INSERT INTO risky_neo_orbits (
                    id, parameters_type, neo_unique_name, epoch_mjd, epoch_as_date, semi_major_axis_a,
                    eccentricity_e, inclination_i, long_of_ascending_node,
                    argument_of_perihelion, mean_anomaly, perihelion_distance,
                    aphelion_distance, asc_node_earth_sep, desc_node_earth_sep,
                    moid, orbital_period, u_parameter, orbit_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', data_tuples)

            # Commit the transaction
            self.conn.commit()

            print(
                f"Successfully inserted {len(orbit_dtos)} NEO orbits into the database.")

        except sqlite3.IntegrityError as e:
            raise DatabaseOperationError(
                f"Integrity error inserting orbit data: {e}")
        except sqlite3.Error as e:
            raise DatabaseOperationError(
                f"Database error inserting orbit data: {e}")
        except TypeError as e:
            raise DatabaseOperationError(f"Invalid data type: {e}")
        finally:
            # Close the connection
            self._close_connection()

    def store_risky_list(self, neos: List[RiskyNEO]):
        """Store the risky NEO list in the database."""
        total_data = len(neos)
        try:
            # Connect to db
            self.conn = sqlite3.connect(
                self.db_name, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            self.cursor = self.conn.cursor()

            # Insert each NEO into the database
            for index, neo in enumerate(neos):
                self._insert_risky_neo(neo)
                # Print progress percentage
                progress = int((index + 1) / total_data * 100)
                sys.stdout.write(
                    f"\rStoring Data in DB: {progress}% completed")
                sys.stdout.flush()

            # Commit the transaction
            self.conn.commit()

            print(f"\n{total_data} NEO stored successfully.")
        except DatabaseOperationError as e:
            print(f"Database Operation Error: {e}")
        finally:
            # Close the connection
            self._close_connection()

    def store_risky_neo_potential_impacts(self, potential_impacts: List[NEOPotentialImpact]):
        """Inserts multiple NEO potential impact records into the risky_neo_potential_impacts table in a batch."""
        try:
            if not isinstance(potential_impacts, list) or not all(isinstance(dto, NEOPotentialImpact) for dto in potential_impacts):
                raise TypeError("Expected a list of NEOPotentialImpact DTOs.")

            # Convert DTOs to a list of tuples for batch insertion
            data_tuples = [dto.as_list() for dto in potential_impacts]

            # Connect to db
            self.conn = sqlite3.connect(
                self.db_name, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            self.cursor = self.conn.cursor()

            # Execute batch insert
            self.cursor.executemany('''
                INSERT INTO risky_neo_potential_impacts (
                    id, neo_unique_name, impact_date_time_utc, mjd, sigma, sigma_imp, 
                    dis_plus_minus_w_re, stretch, ip, expected_energy_mt, ps, ts
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) 
                ON CONFLICT(neo_unique_name, impact_date_time_utc) DO NOTHING
            ''', data_tuples)

            # Commit the transaction
            self.conn.commit()

            print(
                f"Successfully inserted {len(potential_impacts)} NEO potential impacts into the database.")

        except sqlite3.IntegrityError as e:
            raise DatabaseOperationError(
                f"Integrity error inserting potential impact data: {e}")
        except sqlite3.Error as e:
            raise DatabaseOperationError(
                f"Database error inserting potential impact data: {e}")
        except TypeError as e:
            raise DatabaseOperationError(f"Invalid data type: {e}")
        finally:
            # Close the connection
            self._close_connection()

    def get_all_risky_neos(self) -> List[RiskyNEO]:
        """
        Retrieves all records from the risky_neo table.

        :return: List of RiskyNEO objects.
        """
        try:
            # Connect to db
            self.conn = sqlite3.connect(
                self.db_name, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            self.cursor = self.conn.cursor()

            # Retrieve all records from the risky_neo table
            self.cursor.execute("SELECT * FROM risky_neo")
            records = self.cursor.fetchall()

            if not records:
                return []

            return [
                RiskyNEO(
                    unique_name=row[0],
                    diameter_m=row[1],
                    impact_date_time_utc=row[2],
                    ip_max=row[3],
                    ps_max=row[4],
                    ts=row[5],
                    velocity_km_s=row[6],
                    years=row[7],
                    ip_cum=row[8],
                    ps_cum=row[9]
                ) for row in records
            ]

        except sqlite3.Error as e:
            raise DatabaseOperationError(
                f"Failed to retrieve NEO records: {e}")
        finally:
            # Close the connection
            self._close_connection()
    
    def get_neo_by_unique_name(self, unique_name: str):
        """
        Retrieves a NEO record by the unique name.

        :param unique_name: The unique name of the NEO.
        :return: RiskyNEO object.
        """
        try:
            # Connect to db
            self.conn = sqlite3.connect(
                self.db_name, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            self.cursor = self.conn.cursor()

            # Retrieve all records from the risky_neo table
            self.cursor.execute("SELECT * FROM risky_neo WHERE unique_name = ?", (unique_name,))
            record = self.cursor.fetchone()

            if not record:
                return None

            return RiskyNEO(
                unique_name=record[0],
                diameter_m=record[1],
                impact_date_time_utc=record[2],
                ip_max=record[3],
                ps_max=record[4],
                ts=record[5],
                velocity_km_s=record[6],
                years=record[7],
                ip_cum=record[8],
                ps_cum=record[9]
            )
        except sqlite3.Error as e:
            raise DatabaseOperationError(
                f"Failed to retrieve NEO record: {e}")
        finally:
            # Close the connection
            self._close_connection()
            
            
    def get_orbit_by_neo_unique_name(self, neo_unique_name: str):
        """
        Retrieves all NEO orbit records by the NEO unique name.

        :param neo_unique_name: The unique name of the NEO.
        :return: List of NEOOrbit objects.
        """
        try:
            # Connect to db
            self.conn = sqlite3.connect(
                self.db_name, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            self.cursor = self.conn.cursor()

            # Retrieve the single orbit record from the risky_neo_orbits table
            self.cursor.execute(
                "SELECT * FROM risky_neo_orbits WHERE neo_unique_name = ?", (neo_unique_name,))
            record = self.cursor.fetchone()

            if not record:
                return None

            return  NEOOrbit(
                    record_id=record[0],
                    parameters_type=record[1],
                    neo_unique_name=record[2],
                    epoch_mjd=record[3],
                    epoch_as_date=record[4],
                    semi_major_axis_a=record[5],
                    eccentricity_e=record[6],
                    inclination_i=record[7],
                    long_of_ascending_node=record[8],
                    argument_of_perihelion=record[9],
                    mean_anomaly=record[10],
                    perihelion_distance=record[11],
                    aphelion_distance=record[12],
                    asc_node_earth_sep=record[13],
                    desc_node_earth_sep=record[14],
                    moid=record[15],
                    orbital_period=record[16],
                    u_parameter=record[17],
                    orbit_type=record[18]
                    )

        except sqlite3.Error as e:
            raise DatabaseOperationError(
                f"Failed to retrieve NEO orbit records: {e}")
        finally:
            # Close the connection
            self._close_connection()
            
    def get_potential_impacts_by_neo_unique_name(self, neo_unique_name: str):
        """
        Retrieves potential impact records by the NEO unique name.

        :param neo_unique_name: The unique name of the NEO.
        :return: List of NEOPotentialImpact objects.
        """
        try:
            # Connect to db
            self.conn = sqlite3.connect(
                self.db_name, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            self.cursor = self.conn.cursor()

            # Retrieve all records from the risky_neo_potential_impacts table
            self.cursor.execute(
                "SELECT * FROM risky_neo_potential_impacts WHERE neo_unique_name = ? ORDER BY impact_date_time_utc ASC", (neo_unique_name,))
            records = self.cursor.fetchall()

            if not records:
                return []

            return [
                NEOPotentialImpact(
                    record_id=row[0],
                    neo_unique_name=row[1],
                    impact_date_time_utc=row[2],
                    mjd=row[3],
                    sigma=row[4],
                    sigma_imp=row[5],
                    dis_plus_minus_w_re=row[6],
                    stretch=row[7],
                    ip=row[8],
                    expected_energy_mt=row[9],
                    ps=row[10],
                    ts=row[11]
                ) for row in records
            ]

        except sqlite3.Error as e:
            raise DatabaseOperationError(
                f"Failed to retrieve NEO potential impact records: {e}")
        finally:
            # Close the connection
            self._close_connection()
            
    def get_neos_by_impact_dates(self, start_date: datetime, end_date: datetime) -> List[NEOPotentialImpact]:
        """
        Retrieves NEO potential impacts within the specified date range.

        :param start_date: The start date (inclusive, ignoring time).
        :param end_date: The end date (inclusive, ignoring time).
        :return: List of NEOPotentialImpact objects.
        """
        try:
            # Normalize dates to ignore time
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            self.conn = sqlite3.connect(self.db_name, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            self.cursor = self.conn.cursor()

            # Query for records within the date range
            self.cursor.execute(
                """
                SELECT * FROM risky_neo_potential_impacts
                WHERE DATE(impact_date_time_utc) BETWEEN DATE(?) AND DATE(?)
                ORDER BY impact_date_time_utc ASC
                """,
                (start_date, end_date)
            )
            records = self.cursor.fetchall()

            if not records:
                return []

            return [
                NEOPotentialImpact(
                    record_id=row[0],
                    neo_unique_name=row[1],
                    impact_date_time_utc=row[2],
                    mjd=row[3],
                    sigma=row[4],
                    sigma_imp=row[5],
                    dis_plus_minus_w_re=row[6],
                    stretch=row[7],
                    ip=row[8],
                    expected_energy_mt=row[9],
                    ps=row[10],
                    ts=row[11]
                ) for row in records
            ]
        except sqlite3.Error as e:
            raise DatabaseOperationError(f"Failed to retrieve NEOs by impact dates: {e}")
        finally:
            self._close_connection()


    def clear_neo_orbits(self):
        """
        Deletes all records from the risky_neo_orbits table.

        :raises DatabaseOperationError: If deletion fails.
        """
        try:
            # Connect to db
            self.conn = sqlite3.connect(
                self.db_name, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            self.cursor = self.conn.cursor()

            self.cursor.execute("DELETE FROM risky_neo_orbits")
            self.conn.commit()
            print("All records from risky_neo_orbits have been cleared.")
        except sqlite3.Error as e:
            raise DatabaseOperationError(
                f"Failed to clear risky_neo_orbits: {e}")
        finally:
            # Close the connection
            self._close_connection()

    def clear_neo_potential_impacts(self):
        """
        Deletes all records from the risky_neo_potential_impacts table.

        :raises DatabaseOperationError: If deletion fails.
        """
        try:
            # Connect to db
            self.conn = sqlite3.connect(
                self.db_name, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            self.cursor = self.conn.cursor()

            self.cursor.execute("DELETE FROM risky_neo_potential_impacts")
            self.conn.commit()
            print("All records from risky_neo_potential_impacts have been cleared.")
        except sqlite3.Error as e:
            raise DatabaseOperationError(
                f"Failed to clear risky_neo_potential_impacts: {e}")
        finally:
            # Close the connection
            self._close_connection()

    def has_data(self) -> bool:
        """
        Checks if the database contains existing data in any of the key tables.

        :return: True if data exists, False otherwise.
        """
        try:
            tables = ["risky_neo", "risky_neo_orbits", "risky_neo_potential_impacts"]

            # Connect to db
            self.conn = sqlite3.connect(
                self.db_name, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            self.cursor = self.conn.cursor()

            for table in tables:
                self.cursor.execute(f"SELECT EXISTS(SELECT 1 FROM {table} LIMIT 1)")
                if self.cursor.fetchone()[0]:  # If a record exists in any table, return True
                    return True

            return False

        except sqlite3.Error as e:
            raise DatabaseOperationError(f"Error checking database state: {e}")
        finally:
            # Close the connection
            self._close_connection()

    def _create_risky_neo_table(self):
        """Create table for storing NEO risk list overview data."""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS risky_neo (
                    unique_name TEXT PRIMARY KEY,   -- A unique identifier maps the Num/designator.
                    diameter_m REAL,               -- The diameter of the NEO in meters
                    impact_date_time_utc TIMESTAMP,-- The date and time of the potential impact in UTC
                    ip_max REAL,                    -- Impact probability of the max PS solution
                    ps_max REAL,                    -- Max Palermo Scale value of the possible impact solutions
                    ts REAL,                        -- Torino Scale value of the possible impact solutions
                    velocity_km_s REAL,            -- The velocity of the NEO in km/s
                    years TEXT,                     -- Time span of detected impacts
                    ip_cum REAL,                    -- Cumulative probability of all impact solutions
                    ps_cum REAL                     -- Cumulative PS of all impact solutions
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            raise DatabaseOperationError(f"Failed to create table: {e}")

    def _create_risky_neo_orbits_table(self):
        """Create table for storing the NEO orbit properties."""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS risky_neo_orbits (
                    id UUID PRIMARY KEY,            -- A unique identifier of the record
                    parameters_type TEXT,           -- The type of parameters. One of (eq0, eq1, ke0, ke1)
                    neo_unique_name TEXT,           -- A unique identifier maps the Num/designator.
                    epoch_mjd REAL,                 -- The epoch of the orbit in Modified Julian Date
                    epoch_as_date TIMESTAMP,        -- The epoch of the orbit as a date
                    semi_major_axis_a REAL,         -- The semi-major axis of the orbit in AU
                    eccentricity_e REAL,            -- The eccentricity of the orbit
                    inclination_i REAL,             -- The inclination of the orbit in degrees
                    long_of_ascending_node REAL,    -- The longitude of the ascending node in degrees
                    argument_of_perihelion  REAL,   -- The argument of the perihelion in degrees
                    mean_anomaly REAL,              -- The mean anomaly in degrees
                    perihelion_distance REAL,       -- The perihelion distance in AU
                    aphelion_distance REAL,         -- The aphelion distance in AU
                    asc_node_earth_sep REAL,        -- The ascending node - Earth separation in AU
                    desc_node_earth_sep REAL,       -- The descending node - Earth separation in AU
                    moid REAL,                      -- The Minimum Orbit Intersection Distance in AU
                    orbital_period REAL,            -- The orbital period in years
                    u_parameter REAL,               -- The U parameter of the orbit
                    orbit_type TEXT,                -- The type of the orbit. One of (AMOR, APOLLO, ATEN, ATIRA)
                    
                    UNIQUE(parameters_type,neo_unique_name),
                    FOREIGN KEY(neo_unique_name) REFERENCES risky_neo(unique_name)
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            raise DatabaseOperationError(f"Failed to create table: {e}")

    def _create_risky_neo_potential_impacts_table(self):
        """Create table for storing the NEO potential impact data."""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS risky_neo_potential_impacts (
                    id UUID PRIMARY KEY,            -- A unique identifier of the record
                    neo_unique_name TEXT,           -- A unique identifier maps the Num/designator.
                    impact_date_time_utc TIMESTAMP, -- The date and time of the potential impact in UTC
                    mjd REAL,                       -- The Modified Julian Date of the potential impact
                    sigma REAL,                     -- The approximate location along the LOV in sigma space
                    sigma_imp REAL,                 -- The lateral distance from the LOV to the Earth's surface
                    dis_plus_minus_w_re TEXT,       -- The distance between the TP point and the Earth's center
                    stretch REAL,                   -- The stretching is the semimajor axis of confidence region
                    ip REAL,                        -- Impact Probability
                    expected_energy_mt REAL,        -- The expected energy of the impact in mega tonnes of TNT
                    ps REAL,                        -- Palermo Scale value
                    ts REAL,                        -- Torino Scale value
                                
                    UNIQUE(neo_unique_name,impact_date_time_utc),
                    FOREIGN KEY(neo_unique_name) REFERENCES risky_neo(unique_name)
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            raise DatabaseOperationError(f"Failed to create table: {e}")

    def _insert_risky_neo(self, neo_dto: RiskyNEO):
        """Insert parsed NEO risk list data into the database."""
        try:
            if not isinstance(neo_dto, RiskyNEO):
                raise TypeError("Expected an instance of RiskyNEO DTO.")
            self.cursor.execute('''
                INSERT OR REPLACE INTO risky_neo (
                    unique_name, diameter_m, impact_date_time_utc, ip_max, ps_max, ts,
                    velocity_km_s, years, ip_cum, ps_cum
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', neo_dto.as_list())
        except sqlite3.Error as e:
            raise DatabaseOperationError(
                f"Failed to insert data into the database: {e}")

    def _close_connection(self):
        """Close the database connection."""
        try:
            self.conn.close()
        except sqlite3.Error as e:
            raise DatabaseOperationError(
                f"Failed to close database connection: {e}")
