class ImageGenerationException(Exception):
    """Exception raised when image generation fails."""
    
    def __init__(self, message: str, prompt: str = None, error_code: str = None, details: dict = None):
        """
        Initialize the ImageGenerationException.

        :param message: A string describing the image generation error.
        :param prompt: The prompt that was used for image generation.
        :param error_code: API or system error code if available.
        :param details: Optional dictionary containing additional error details.
        """
        super().__init__(message)
        self.prompt = prompt
        self.error_code = error_code
        self.details = details or {}

    def __str__(self):
        """Return a formatted string representation of the exception."""
        base_msg = self.args[0]
        if self.error_code:
            base_msg += f" (Error code: {self.error_code})"
        if self.prompt:
            base_msg += f" | Prompt: {self.prompt[:100]}..."
        if self.details:
            base_msg += f" | Details: {self.details}"
        return base_msg
