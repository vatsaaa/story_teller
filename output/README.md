# Output Folder Structure

This folder contains all generated content from the Story Teller application.

## Directory Structure

```
output/
├── README.md           # This documentation file
├── audios/             # Generated audio files
├── videos/             # Generated video files with embedded audio
└── images/             # Generated or processed story images
```

## Content Description

### 📁 `audios/`
Contains audio files generated from story text using Text-to-Speech (TTS):
- **Format**: MP3 files
- **Language**: Hindi (primary) and English
- **Content**: Complete story narration including introduction and conclusion
- **Naming**: `{story_name}_{story_id}.mp3`

### 📁 `videos/`
Contains video files with synchronized audio and visual content:
- **Format**: MP4 files with embedded audio
- **Video**: Image slideshow with story-related scenes
- **Audio**: Synchronized TTS narration
- **Resolution**: 800x600 pixels
- **Frame Rate**: 24 FPS
- **Duration**: Matches audio duration exactly
- **Naming**: `{story_name}_{story_id}.mp4`

### 📁 `images/`
Contains generated or processed images for story visualization:
- **Format**: PNG/JPG files
- **Content**: Scene-based images representing story elements
- **Processing**: Resized and optimized for video generation
- **Usage**: Combined into video slideshows

## Usage Notes

- All files are generated automatically by the application
- Audio and video files are synchronized for seamless playback
- Generated content is ready for social media publishing
- Files can be used independently or as part of the complete story package

## File Management

- Generated files are organized by story ID to avoid conflicts
- Old files may be overwritten when regenerating content for the same story
- Manual cleanup may be needed for storage management
