class StoryProcessingException(Exception):
    """Exception raised when story processing (sceneries extraction, content parsing) fails."""
    
    def __init__(self, message: str, processing_step: str = None, details: dict = None):
        """
        Initialize the StoryProcessingException.

        :param message: A string describing the story processing error.
        :param processing_step: The specific processing step that failed (e.g., 'scenery_extraction', 'content_parsing').
        :param details: Optional dictionary containing additional error details.
        """
        super().__init__(message)
        self.processing_step = processing_step
        self.details = details or {}

    def __str__(self):
        """Return a formatted string representation of the exception."""
        base_msg = self.args[0]
        if self.processing_step:
            base_msg += f" (Step: {self.processing_step})"
        if self.details:
            base_msg += f" | Details: {self.details}"
        return base_msg
