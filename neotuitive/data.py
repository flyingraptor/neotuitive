import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed 
from datetime import datetime, timedelta
from typing import List

from .db.repository import NeoRiskListDB, RiskyNEO, NEOOrbit, NEOPotentialImpact
from .api.handler import NeoRiskListAPI, NeoRiskListAPIError


class DataLoaderError(Exception):
    """Base class for exceptions in the DataLoader."""


class DataParsingError(DataLoaderError):
    """Exception raised for errors during data parsing."""


class StorageOperationError(DataLoaderError):
    """Exception raised for errors during interacting with storage."""


class InvalidProbabilityError(DataLoaderError):
    """Exception raised for invalid probability values."""


class DataLoader:
    """Handles data loading operations for Near-Earth Object (NEO) risk list."""

    def __init__(self, source: NeoRiskListAPI, target: NeoRiskListDB):
        self.source = source
        self.target = target

    def fetch_and_store_risk_list(self):
        """Fetch risk list from API and store it in the database."""
        try:
            raw_data = self.source.get_risk_list()
            parsed_data = self._parse_risk_list(raw_data)

            if not parsed_data:
                raise DataParsingError("Parsed data is empty.")

            risky_neos = self._map_parsed_data_to_neo_risk_objects(parsed_data)
            self.target.store_risky_list(risky_neos)
        except (NeoRiskListAPIError, DataParsingError, StorageOperationError, ValueError, KeyError, TypeError) as e:
            print(f"Error: {e}")
            
    def fetch_and_store_orbits(self, max_workers=None):
        """
        Fetches orbit properties for all risky NEOs using multiple threads and stores them in the storage in bulk.

        :param max_workers: Number of threads to use for parallel API calls. None value lets Python decide.
        """
        try:

            # Step 0: Clear existing orbit data
            self.target.clear_neo_orbits()

            # Step 1: Retrieve all risky NEOs
            risky_neos = self.target.get_all_risky_neos()
            if not risky_neos:
                print("No risky NEOs found in the database.")
                return

            total_neos = len(risky_neos)
            orbit_dtos = []  # List to store all orbit DTOs

            # Step 2: Define function for threaded execution
            def fetch_orbit(neo):
                """Fetch and parse orbit properties for a single NEO."""
                try:
                    raw_orbit_data = self.source.get_orbit_properties(
                        neo.unique_name)
                    return self._parse_orbit_data(neo.unique_name, raw_orbit_data)
                except (NeoRiskListAPIError, DataParsingError) as e:
                    print(f"Error processing {neo.unique_name}: {e}")
                    return None  # Skip failed requests

            # Step 3: Run API calls in parallel
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_neo = {executor.submit(
                    fetch_orbit, neo): neo for neo in risky_neos}

                for index, future in enumerate(as_completed(future_to_neo)):
                    orbit_dto = future.result()
                    if orbit_dto:
                        # Add to list if successful
                        orbit_dtos.append(orbit_dto)

                    # Print progress
                    progress = int((index + 1) / total_neos * 100)
                    sys.stdout.write(
                        f"\rFetching Orbit Data: {progress}% completed")
                    sys.stdout.flush()

            print("\nAll orbit data retrieved. Inserting into database...")

            # Step 4: Insert all collected orbit data at once
            if orbit_dtos:
                self.target.store_risky_neo_orbits(orbit_dtos)

        except StorageOperationError as e:
            print(f"Database Operation Error: {e}")

    def fetch_and_store_potential_impacts(self, max_workers=None):
        """
        Fetches potential impact data for all risky NEOs using multiple threads and stores them in the database in bulk.

        :param max_workers: Number of threads to use for parallel API calls. None value lets Python decide.
        """
        try:
            # Step 0: Clear existing potential impacts data
            self.target.clear_neo_potential_impacts()

            # Step 1: Retrieve all risky NEOs
            risky_neos = self.target.get_all_risky_neos()
            if not risky_neos:
                print("No risky NEOs found in the database.")
                return

            total_neos = len(risky_neos)
            impact_dtos = []  # List to store all potential impact DTOs

            # Step 2: Define function for threaded execution
            def fetch_potential_impacts(neo):
                """Fetch and parse potential impact data for a single NEO."""
                try:
                    raw_impact_data = self.source.get_potential_impacts(
                        neo.unique_name)
                    return self._parse_potential_impact_data(neo.unique_name, raw_impact_data)
                except (NeoRiskListAPIError, DataParsingError) as e:
                    print(f"Error processing {neo.unique_name}: {e}")
                    return []  # Return empty list for failed requests

            # Step 3: Run API calls in parallel and track progress
            sys.stdout.write("\rFetching Potential Impacts: 0% completed")
            sys.stdout.flush()
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                results = executor.map(
                    fetch_potential_impacts, risky_neos)  # Fetch in parallel

                total_neos = len(risky_neos)  # Total number of NEOs
                impact_dtos = []  # Store results

                # Track progress
                for index, impact_dto_list in enumerate(results, start=1):
                    if impact_dto_list:
                        # Append successful results
                        impact_dtos.extend(impact_dto_list)

                    # Print progress every 50 items (adjust as needed)
                    if index % 50 == 0 or index == total_neos:
                        progress = int((index / total_neos) * 100)
                        sys.stdout.write(
                            f"\rFetching Potential Impacts: {progress}% completed")
                        sys.stdout.flush()

            print("\nAll potential impact data retrieved. Inserting into database...")

            # Step 4: Insert all collected impact data at once
            if impact_dtos:
                self.target.store_risky_neo_potential_impacts(impact_dtos)

        except StorageOperationError as e:
            print(f"Database Operation Error: {e}")

    def initialize_storage(self, refresh=False):
        """
        Checks if the storage is initialized. If not, loads all data.
        """
        if not self.target.has_data():
            print("Storage is empty. Loading data...")
            refresh = True  # Force refresh if empty
        elif refresh:
            print("Refreshing storage data...")
        else:
            print("Storage is already initialized. Skipping data loading.")
            return  # Skip loading if data exists
        
        self.fetch_and_store_risk_list()
        self.fetch_and_store_orbits()
        self.fetch_and_store_potential_impacts()

    def _parse_risk_list(self, raw_data: str) -> List[tuple]:
        """Parses the plain text risk list into structured tuples."""
        try:
            parsed_data = []
            lines = raw_data.strip().split("\n")[4:]

            for line in lines:
                if line.strip():
                    parts = re.split(r"\s+\|\s+", line.strip())

                    if re.search("\|\s+\|", line):
                        parts.insert(2, "no useful value")

                    if len(parts) != 11:
                        raise DataParsingError(
                            f"Unexpected data format in line: {line}")

                    parts = [self._clear_data_point(p) for p in parts]

                    parsed_data.append((
                        parts[0],
                        float(parts[1]),
                        self._validate_regular_date_time(parts[3]),
                        self._validate_probability(parts[4]),
                        float(parts[5]),
                        float(parts[6]),
                        float(parts[7]),
                        parts[8],
                        self._validate_probability(parts[9]),
                        float(parts[10].removesuffix("|").strip())
                    ))
            return parsed_data
        except ValueError as e:
            raise DataParsingError(
                f"Failed to convert data types while parsing: {e}") from e

    def _clear_data_point(self, data_point: str) -> str:
        """Removes unnecessary characters from data points."""
        return data_point.strip("|").strip()

    def _validate_probability(self, value: str) -> float:
        """Ensures probability is between 0 and 1."""
        try:
            probability = float(value)
            if not (0 <= probability <= 1):
                raise InvalidProbabilityError(
                    f"Probability value {probability} out of bounds (0-1).")
            return probability
        except ValueError as exc:
            raise DataParsingError(f"Invalid probability value: {value}") from exc

    def _validate_regular_date_time(self, value: str) -> str:
        """Validates and ensures correct date-time format."""
        try:
            datetime.strptime(value, "%Y-%m-%d %H:%M")
            return value
        except ValueError as exc:
            raise DataParsingError(
                f"Incorrect data format {value}, should be YYYY-MM-DD HH:MM") from exc

    def _map_parsed_data_to_neo_risk_objects(self, parsed_data: List[tuple]) -> List[RiskyNEO]:
        """Maps parsed data to RiskyNEO objects."""
        return [
            RiskyNEO(data[0], data[1], datetime.strptime(data[2], "%Y-%m-%d %H:%M"), data[3],
                     data[4], data[5], data[6], data[7], data[8], data[9])
            for data in parsed_data
        ]

    def _parse_orbit_data(self, neo_unique_name: str, raw_data: str) -> NEOOrbit:
        """
        Parses the raw orbit data response and maps it to an NEOOrbit DTO.

        :param neo_unique_name: The unique name of the NEO.
        :param raw_data: The raw text response containing orbit properties.
        :return: NEOOrbit DTO.
        """
        try:
            lines = raw_data.strip().split("\n")
            if len(lines) < 10:
                raise DataParsingError(
                    f"Insufficient orbit data for {neo_unique_name}")

            semi_major_axis_a = None
            eccentricity_e = None
            inclination_i = None
            long_of_ascending_node = None
            argument_of_perihelion = None
            mean_anomaly = None
            epoch_mjd = None
            perihelion_distance = None
            aphelion_distance = None
            asc_node_earth_sep = None
            desc_node_earth_sep = None
            moid = None
            orbital_period = None
            u_parameter = None
            orbit_type = None

            for line in lines:
                line = line.strip()

                if line.startswith("KEP"):
                    parts = line.split()
                    semi_major_axis_a = float(parts[1])
                    eccentricity_e = float(parts[2])
                    inclination_i = float(parts[3])
                    long_of_ascending_node = float(parts[4])
                    argument_of_perihelion = float(parts[5])
                    mean_anomaly = float(parts[6])

                elif line.startswith("MJD"):
                    epoch_mjd = float(line.split()[1])

                elif line.startswith("! PERIHELION"):
                    perihelion_distance = float(line.split()[2])

                elif line.startswith("! APHELION"):
                    aphelion_distance = float(line.split()[2])

                elif line.startswith("! ANODE"):
                    asc_node_earth_sep = float(line.split()[2])

                elif line.startswith("! DNODE"):
                    desc_node_earth_sep = float(line.split()[2])

                elif line.startswith("! MOID"):
                    moid = float(line.split()[2])

                elif line.startswith("! PERIOD"):
                    orbital_period = float(line.split()[2])

                elif line.startswith("! U_PAR"):
                    u_parameter = float(line.split()[2])

                elif line.startswith("! ORB_TYPE"):
                    orbit_type = line.split()[2]

            if None in [semi_major_axis_a, eccentricity_e, inclination_i, long_of_ascending_node,
                        argument_of_perihelion, mean_anomaly, epoch_mjd, perihelion_distance,
                        aphelion_distance, asc_node_earth_sep, desc_node_earth_sep, moid,
                        orbital_period, u_parameter, orbit_type]:
                raise DataParsingError(
                    f"Incomplete orbit data for {neo_unique_name}")

            return NEOOrbit(
                parameters_type="ke0",
                neo_unique_name=neo_unique_name,
                epoch_mjd=epoch_mjd,
                epoch_as_date=self._convert_epoch_mjd_to_datetime(epoch_mjd),
                semi_major_axis_a=semi_major_axis_a,
                eccentricity_e=eccentricity_e,
                inclination_i=inclination_i,
                long_of_ascending_node=long_of_ascending_node,
                argument_of_perihelion=argument_of_perihelion,
                mean_anomaly=mean_anomaly,
                perihelion_distance=perihelion_distance,
                aphelion_distance=aphelion_distance,
                asc_node_earth_sep=asc_node_earth_sep,
                desc_node_earth_sep=desc_node_earth_sep,
                moid=moid,
                orbital_period=orbital_period,
                u_parameter=u_parameter,
                orbit_type=orbit_type
            )

        except ValueError as e:
            raise DataParsingError(
                f"Failed to parse orbit data for {neo_unique_name}: {e}") from e

    def _parse_potential_impact_data(self, neo_unique_name: str, raw_data: str) -> List[NEOPotentialImpact]:
        """
        Parses the raw potential impact data response and maps it to a list of NEOPotentialImpact DTOs.

        :param neo_unique_name: The unique name of the NEO.
        :param raw_data: The raw text response containing potential impact data.
        :return: List of NEOPotentialImpact DTOs.
        """
        try:
            lines = raw_data.strip().split("\n")
            impact_dtos = []

            data_section = False
            for line in lines:
                line = line.strip()

                # Identify when data starts (first line containing date)
                if re.match(r"\d{4}-\d{2}-\d{2}", line):
                    data_section = True
                else:
                    data_section = False

                if data_section and line:
                    parts = re.split(r"\s+", line)
                    if len(parts) < 11:
                        continue  # Skip malformed lines
                    impact_date = self._convert_fractional_date(parts[0])
                    mjd = self._safe_float(parts[1])
                    sigma = self._safe_float(parts[2])
                    sigma_imp = self._safe_float(parts[3])
                    dis_plus_minus_w_re = ''.join(
                        (parts[4], parts[5], parts[6]))
                    stretch = self._safe_float(parts[7])
                    ip = self._safe_float(parts[8])
                    expected_energy_mt = self._safe_float(parts[9])
                    ps = self._safe_float(parts[10])
                    ts = self._safe_float(parts[11])

                    impact_dtos.append(NEOPotentialImpact(
                        neo_unique_name=neo_unique_name,
                        impact_date_time_utc=impact_date,
                        mjd=mjd,
                        sigma=sigma,
                        sigma_imp=sigma_imp,
                        dis_plus_minus_w_re=dis_plus_minus_w_re,
                        stretch=stretch,
                        ip=ip,
                        expected_energy_mt=expected_energy_mt,
                        ps=ps,
                        ts=ts
                    ))

            return impact_dtos

        except ValueError as e:
            raise DataParsingError(
                f"Failed to parse potential impact data for {neo_unique_name}: {e}") from e

    def _convert_epoch_mjd_to_datetime(self, mjd: float) -> datetime:
        """
        Converts Modified Julian Date (MJD) to a standard UTC datetime.

        :param mjd: Modified Julian Date (float)
        :return: Converted datetime object in UTC
        :raises ValueError: If the input is not a valid number.
        """
        try:
            # MJD epoch starts from November 17, 1858
            mjd_epoch = datetime(1858, 11, 17)

            # Convert MJD to UTC datetime
            converted_datetime = mjd_epoch + timedelta(days=mjd)

            return converted_datetime
        except Exception as e:
            raise ValueError(f"Invalid MJD value: {mjd}, error: {e}") from e

    def _convert_fractional_date(self, date_str: str) -> datetime:
        """
        Converts a date string with a fractional day (YYYY-MM-DD.DDD) to a datetime object.

        :param date_str: String date in format 'YYYY-MM-DD.DDD'
        :return: Corresponding datetime object.
        """
        try:
            # Split the date part (YYYY-MM-DD) and the fractional day (.DDD)
            date_part, fraction_part = date_str.split(".")

            # Convert the base date to a datetime object
            base_date = datetime.strptime(date_part, "%Y-%m-%d")

            # Convert the fractional part to seconds
            fraction_of_day = float("0." + fraction_part)
            seconds_in_day = 86400  # Total seconds in a day
            additional_seconds = fraction_of_day * seconds_in_day

            # Add the fractional day as a timedelta
            final_datetime = base_date + timedelta(seconds=additional_seconds)

            return final_datetime

        except ValueError as e:
            raise ValueError(f"Invalid date format: {date_str}, error: {e}") from e

    def _safe_float(self, value: str):
        """
        Safely converts a string to a float. If conversion fails, returns None.

        :param value: The input string to convert.
        :return: Float value if valid, otherwise None.
        """
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
