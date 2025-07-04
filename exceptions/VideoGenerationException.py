class VideoGenerationException(Exception):
    """Exception raised when video generation fails."""
    
    def __init__(self, message: str, method: str = None, details: dict = None):
        """
        Initialize the VideoGenerationException.

        :param message: A string describing the video generation error.
        :param method: The video generation method that was used.
        :param details: Optional dictionary containing additional error details.
        """
        super().__init__(message)
        self.method = method
        self.details = details or {}

    def __str__(self):
        """Return a formatted string representation of the exception."""
        base_msg = self.args[0]
        if self.method:
            base_msg += f" (Method: {self.method})"
        if self.details:
            base_msg += f" | Details: {self.details}"
        return base_msg
