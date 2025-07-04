class AudioGenerationException(Exception):
    """Exception raised when audio generation fails."""
    
    def __init__(self, message: str, library: str = None, language: str = None, details: dict = None):
        """
        Initialize the AudioGenerationException.

        :param message: A string describing the audio generation error.
        :param library: The TTS library that was used.
        :param language: The language code for TTS.
        :param details: Optional dictionary containing additional error details.
        """
        super().__init__(message)
        self.library = library
        self.language = language
        self.details = details or {}

    def __str__(self):
        """Return a formatted string representation of the exception."""
        base_msg = self.args[0]
        if self.library:
            base_msg += f" (Library: {self.library})"
        if self.language:
            base_msg += f" (Language: {self.language})"
        if self.details:
            base_msg += f" | Details: {self.details}"
        return base_msg
