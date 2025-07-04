from exceptions import VideoGenerationException
import os
from moviepy.editor import ImageSequenceClip, AudioFileClip, ImageClip, concatenate_videoclips
from PIL import Image as PILImage

class Video:
    def __init__(self, file_path: str, file_name: str):
        self.file_path = file_path
        self.file_name = file_name

        if not self.file_path:
            os.makedirs(file_path, exist_ok=True)

    def generate(self, name: str, video_path: str, image_paths: list):
        # Ensure the output videos directory exists
        video_dir = './output/videos'
        if not os.path.exists(video_dir):
            os.makedirs(video_dir, exist_ok=True)

        video_name = f'{name}.mp4'
        self.file_path = os.path.join('./output/videos', video_name)

        try:
            # Validate input
            if not image_paths:
                raise VideoGenerationException(
                    "No image paths provided for video generation",
                    details={"image_count": 0}
                )
            
            # Check if image files actually exist
            existing_images = [img_path for img_path in image_paths if os.path.exists(img_path)]
            if not existing_images:
                raise VideoGenerationException(
                    "None of the provided image files exist",
                    details={"provided_paths": image_paths}
                )
            
            # Prepare images for video creation
            temp_dir = tempfile.mkdtemp()
            processed_images = []
            
            for i, img_path in enumerate(existing_images):
                try:
                    # Open and resize each image
                    img = PILImage.open(img_path)
                    img = img.resize((800, 600)).convert('RGB')  # Ensure consistent size and format
                    
                    # Save processed image to temp directory
                    temp_img_path = os.path.join(temp_dir, f"img_{i:03d}.jpg")
                    img.save(temp_img_path)
                    processed_images.append(temp_img_path)
                except Exception as e:
                    print(f"Warning: Failed to process image {img_path}: {e}")
                    continue
            
            if not processed_images:
                raise VideoGenerationException(
                    "Failed to process any images for video generation",
                    details={"attempted_images": len(existing_images)}
                )
            
            # Create video from images with better audio synchronization
            fps = 24
            
            # First, get audio duration to plan video timing
            audio_duration = None
            if os.path.exists(audio_path):
                temp_audio_clip = AudioFileClip(audio_path)
                audio_duration = temp_audio_clip.duration
                temp_audio_clip.close()  # Close to free memory
            
            if audio_duration and len(processed_images) > 0:
                # Calculate duration per image to match audio length
                num_images = len(processed_images)
                duration_per_image = audio_duration / num_images
                # Ensure minimum duration per image (at least 1 second)
                duration_per_image = max(duration_per_image, 1.0)
                
                print(f"Audio duration: {audio_duration:.1f}s, Images: {num_images}, Duration per image: {duration_per_image:.1f}s")
                
                # Create individual image clips with specific durations
                from moviepy.editor import ImageClip, concatenate_videoclips
                image_clips = []
                
                for img_path in processed_images:
                    clip = ImageClip(img_path).set_duration(duration_per_image).set_fps(fps)
                    image_clips.append(clip)
                
                # Concatenate all image clips
                video_clip = concatenate_videoclips(image_clips, method="compose")
                
            else:
                # No audio or no images, use default timing
                duration_per_image = 3.0  # seconds per image
                from moviepy.editor import ImageClip, concatenate_videoclips
                image_clips = []
                
                for img_path in processed_images:
                    clip = ImageClip(img_path).set_duration(duration_per_image).set_fps(fps)
                    image_clips.append(clip)
                
                video_clip = concatenate_videoclips(image_clips, method="compose")
            
            # Add audio and ensure perfect synchronization
            if path.exists(audio_path):
                # Create a fresh audio clip for final composition
                audio_clip = AudioFileClip(audio_path)
                
                print(f"Video duration: {video_clip.duration:.1f}s, Audio duration: {audio_clip.duration:.1f}s")
                
                # Ensure video and audio have exactly the same duration
                if abs(video_clip.duration - audio_clip.duration) > 0.1:  # If difference > 0.1 seconds
                    if video_clip.duration > audio_clip.duration:
                        # Trim video to match audio
                        video_clip = video_clip.subclip(0, audio_clip.duration)
                        print(f"Trimmed video to {audio_clip.duration:.1f}s")
                    else:
                        # Trim audio to match video duration
                        audio_clip = audio_clip.subclip(0, video_clip.duration)
                        print(f"Trimmed audio to {video_clip.duration:.1f}s")
                
                # Combine video and audio
                final_video = video_clip.set_audio(audio_clip)
            else:
                final_video = video_clip
            
            # Write the final video with proper cleanup
            final_video.write_videofile(
                self.path,
                fps=fps,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            # Clean up clips to free memory
            final_video.close()
            video_clip.close()
            
            # Clean up temporary files
            for temp_file in processed_images:
                if path.exists(temp_file):
                    os.remove(temp_file)
            os.rmdir(temp_dir)
            
        except Exception as e:
            raise VideoGenerationException(
                f"Video generation failed: {str(e)}",
                method="moviepy",
                details={
                    "error": str(e), 
                    "audio_path": audio_path, 
                    "image_count": len(image_paths),
                    "output_path": self.path
                }
            )

        return self.path