class Config:
    """
    Configuration settings for the core of Nyrkiö

    Args:
        min_magnitude (float): The minimum magnitude of a performance change, expressed as a percentage
        max_pvalue (float): The maximum p-value for a performance change to be considered significant
    """

    def __init__(self, min_magnitude=0.05, max_pvalue=0.001):
        self.min_magnitude = min_magnitude
        self.max_pvalue = max_pvalue
