import requests


class NeoRiskListAPIError(Exception):
    """Base class for exceptions in the NeoRiskListAPI."""

class NeoRiskListAPIConnectionError(NeoRiskListAPIError):
    """Raised when there is a connection issue."""


class NeoRiskListAPIResponseError(NeoRiskListAPIError):
    """Raised when the API response contains an error."""


class NeoRiskListAPI:
    """Handles interaction with the ESA Neo Risk List API."""

    BASE_URL = "https://neo.ssa.esa.int"

    def __init__(self):
        self.session = requests.Session()

    def _get(self, endpoint: str) -> str:
        """Internal method to make GET requests to the API."""
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.exceptions.ConnectionError as exc:
            raise NeoRiskListAPIConnectionError(
                "Failed to connect to the Neo Risk List API.") from exc
        except requests.exceptions.HTTPError as err:
            raise NeoRiskListAPIResponseError(f"API returned an error: {err}") from err
        except requests.exceptions.RequestException as err:
            raise NeoRiskListAPIError(f"An unexpected error occurred: {err}") from err

    def get_risk_list(self) -> str:
        """Fetches the current list of NEOs in the risk list."""
        return self._get("/PSDB-portlet/download?file=esa_risk_list")

    def get_orbit_properties(self, neo_unique_name: str) -> str:
        """
        Fetches the orbit properties of a specific NEO.

        :param neo_unique_name: The unique name of the NEO.
        :return: Raw text response containing orbit properties.
        """
        endpoint = f"/PSDB-portlet/download?file={neo_unique_name}.ke0"
        return self._get(endpoint)

    def get_potential_impacts(self, neo_unique_name: str) -> str:
        """
        Fetches the potential impact data for a specific NEO.

        :param neo_unique_name: The unique name of the NEO.
        :return: Raw text response containing potential impact data.
        :raises NeoRiskListAPIError: If the request fails.
        """
        endpoint = f"/PSDB-portlet/download?file={neo_unique_name}.risk"
        return self._get(endpoint)
