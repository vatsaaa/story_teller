class ConfigurationException(Exception):
    """Exception raised when there are configuration-related errors."""
    
    def __init__(self, message: str, config_key: str = None, details: dict = None):
        """
        Initialize the ConfigurationException.

        :param message: A string describing the configuration error.
        :param config_key: The specific configuration key that caused the error.
        :param details: Optional dictionary containing additional error details.
        """
        super().__init__(message)
        self.config_key = config_key
        self.details = details or {}

    def __str__(self):
        """Return a formatted string representation of the exception."""
        base_msg = self.args[0]
        if self.config_key:
            base_msg += f" (Config key: {self.config_key})"
        if self.details:
            base_msg += f" | Details: {self.details}"
        return base_msg
