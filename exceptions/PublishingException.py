class PublishingException(Exception):
    """Exception raised when publishing to social media platforms fails."""
    
    def __init__(self, message: str, platform: str = None, error_code: str = None, details: dict = None):
        """
        Initialize the PublishingException.

        :param message: A string describing the publishing error.
        :param platform: The social media platform (Facebook, Instagram, Twitter, YouTube).
        :param error_code: Platform-specific error code if available.
        :param details: Optional dictionary containing additional error details.
        """
        super().__init__(message)
        self.platform = platform
        self.error_code = error_code
        self.details = details or {}

    def __str__(self):
        """Return a formatted string representation of the exception."""
        base_msg = self.args[0]
        if self.platform:
            base_msg += f" (Platform: {self.platform})"
        if self.error_code:
            base_msg += f" (Error code: {self.error_code})"
        if self.details:
            base_msg += f" | Details: {self.details}"
        return base_msg
