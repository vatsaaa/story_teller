# Exception Handling Documentation

## Overview

The Story Teller application now uses specific exception types instead of generic exceptions to provide better error handling and debugging capabilities.

## Exception Types

### ConfigurationException
- **Purpose**: Configuration-related errors (missing API keys, invalid settings)
- **Location**: `exceptions/ConfigurationException.py`
- **Usage**: When environment variables or configuration files are missing or invalid
- **Example**: Missing `TEXT_TO_IMAGE_URL`, `AIHORDE_API_KEY`, `STABLEDIFFUSION_API_KEY_FILE`

### ImageGenerationException
- **Purpose**: Image generation failures
- **Location**: `exceptions/ImageGenerationException.py`
- **Usage**: When AI Horde, Stable Diffusion, or other image generation services fail
- **Example**: API request failures, no image data returned, invalid prompts

### TranslationException
- **Purpose**: Translation and text processing errors
- **Location**: `exceptions/TranslationException.py`
- **Usage**: When LLM translation fails or content is missing
- **Example**: Missing Hindi content, LLM API failures during translation

### AudioGenerationException
- **Purpose**: Text-to-speech and audio generation errors
- **Location**: `exceptions/AudioGenerationException.py`
- **Usage**: When gTTS, pyttsx3, or other TTS libraries fail
- **Example**: Invalid TTS library, audio file creation failures

### VideoGenerationException
- **Purpose**: Video creation and processing errors
- **Location**: `exceptions/VideoGenerationException.py`
- **Usage**: When moviepy or video processing fails
- **Example**: Invalid audio/image files, video encoding errors

### PublishingException
- **Purpose**: Social media publishing errors
- **Location**: `exceptions/PublishingException.py`
- **Usage**: When publishing to Facebook, Instagram, Twitter, or YouTube fails
- **Example**: Invalid credentials, API rate limits, upload failures

### StoryProcessingException
- **Purpose**: Story content processing errors
- **Location**: `exceptions/StoryProcessingException.py`
- **Usage**: When scenery extraction, content parsing, or story processing fails
- **Example**: LLM output parsing errors, invalid story format

## Migration from CustomException

The application has been refactored to replace generic `CustomException` usage with specific exception types:

### Before
```python
raise CustomException("Image generation failed", details={"error": str(e)})
```

### After
```python
raise ImageGenerationException(
    "Image generation failed", 
    prompt=prompt[:100] + "...",
    details={"error": str(e), "method": "aihorde"}
)
```

## Benefits

1. **Better Error Identification**: Specific exception types make it easier to identify the source of errors
2. **Improved Debugging**: Additional context fields (like `prompt`, `platform`, `config_key`) provide more debugging information
3. **Targeted Error Handling**: Different exception types can be handled differently in UI and logging
4. **Better User Experience**: More specific error messages can guide users to solutions

## Usage in Streamlit UI

The Streamlit pages can now catch specific exceptions and provide targeted user guidance:

```python
try:
    story.get_images()
except ConfigurationException as e:
    st.error(f"Configuration Error: {e}")
    st.info("Please check your .env file and ensure all required API keys are set.")
except ImageGenerationException as e:
    st.error(f"Image Generation Failed: {e}")
    st.warning("Try again or check your image generation service status.")
```

## Future Enhancements

- Add logging integration with specific exception types
- Implement retry mechanisms for specific exception types
- Add metrics and monitoring for different error categories
- Create user-friendly error recovery suggestions
