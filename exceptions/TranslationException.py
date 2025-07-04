class TranslationException(Exception):
    """Exception raised when translation or text processing fails."""
    
    def __init__(self, message: str, source_lang: str = None, target_lang: str = None, details: dict = None):
        """
        Initialize the TranslationException.

        :param message: A string describing the translation error.
        :param source_lang: The source language code.
        :param target_lang: The target language code.
        :param details: Optional dictionary containing additional error details.
        """
        super().__init__(message)
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.details = details or {}

    def __str__(self):
        """Return a formatted string representation of the exception."""
        base_msg = self.args[0]
        if self.source_lang and self.target_lang:
            base_msg += f" ({self.source_lang} -> {self.target_lang})"
        if self.details:
            base_msg += f" | Details: {self.details}"
        return base_msg
