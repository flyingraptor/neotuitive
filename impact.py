class ImpactError(Exception):
    """Base class for exceptions in this module."""

class InvalidProbabilityError(ImpactError):
    """Exception raised for errors in the probability value."""
    def __init__(self, probability, message="Probability must be between 0 and 1"):
        self.probability = probability
        self.message = message
        super().__init__(self.message)

class PossibleImpact:
    """ 
    A class to represent a possible impact event. 
    
    Attributes
    ----------
    datetime_utc : datetime
        The date and time of the possible impact event in UTC.
    probability : float
        The probability of the impact event.
    expected_energy_in_mt : float
        The expected energy of the impact event in megatons.
    """
    
    def __init__(self, datetime_utc, probability, expected_energy_in_mt):
        self._datetime_utc = datetime_utc
        self._probability = probability
        self._expected_energy_in_mt = expected_energy_in_mt

    def __str__(self):
        return f"   Datetime in UTC: {self.datetime_utc} Probability: {self.probability} Expected Energy: {self.expected_energy_in_mt}\n"
    
    @property
    def datetime_utc(self):
        return self._datetime_utc
    
    @datetime_utc.setter
    def datetime_utc(self, datetime_utc):
        self._datetime_utc = datetime_utc
        return self
    
    @property
    def probability(self):
        return self._probability
    
    @probability.setter
    def probability(self, probability):
        if probability < 0 or probability > 1:
            raise InvalidProbabilityError(probability)
        self._probability = probability
        return self
    
    @property
    def expected_energy_in_mt(self):
        return self._expected_energy_in_mt
    
    @expected_energy_in_mt.setter
    def expected_energy_in_mt(self, expected_energy_in_mt):
        self._expected_energy_in_mt = expected_energy_in_mt
        return self