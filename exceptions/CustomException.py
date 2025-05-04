class CustomException(Exception):
    def __init__(self, message: str, details: dict = None):
        """
        Initialize the CustomException with a message and optional details.

        :param message: A string describing the error.
        :param details: Optional dictionary containing additional error details.
        """
        super().__init__(message)
        self.details = details

    def __str__(self):
        """
        Return a formatted string representation of the exception.
        """
        if self.details:
            return f"{self.args[0]} | Details: {self.details}"
        return self.args[0]

