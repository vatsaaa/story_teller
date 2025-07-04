import streamlit as st
import os
from exceptions import VideoGenerationException

st.title("🎥 Video Generation")

if st.session_state.get('story'):
    story = st.session_state.get('story', None)
    
    # Show some info about the story
    if hasattr(story, 'texts') and story.texts:
        if 'Hindi' in story.texts:
            st.info(f"**Story Title:** {story.texts['Hindi'].title}")
    
    # Check if video already exists without trying to generate it
    video_exists = False
    current_video_file = None
    
    try:
        # Check if video is already available
        if hasattr(story, 'video') and story.video and hasattr(story.video, 'path') and story.video.path:
            current_video_file = story.video.path
            video_exists = os.path.exists(current_video_file)
        else:
            # Try to get a reasonable video filename based on story
            story_name = getattr(story, 'name', None)
            if story_name:
                potential_file = f"./output/videos/{story_name}.mp4"
                if os.path.exists(potential_file):
                    current_video_file = potential_file
                    video_exists = True
    except Exception:
        video_exists = False

    if video_exists and current_video_file:
        with st.form(key='video_form'):
            st.video(current_video_file, format="video/mp4", start_time=0)
            
            st.write("---")
            st.subheader("Next Steps")
            submit_video = st.form_submit_button(label='📤 Publish to Social Media')
            
            if submit_video:
                try:
                    from publishers.PublisherFactory import get_publishers
                    
                    # Get the main args from session state
                    mainargs = st.session_state.get('mainargs', {})
                    
                    with st.spinner("Publishing to selected platforms..."):
                        publishers = get_publishers(mainargs)
                        if publishers:
                            story.publish(publishers=publishers)
                            st.success("Story published successfully!")
                            st.balloons()
                        else:
                            st.warning("No publishers configured. Please check your social media settings in the .env file.")
                            
                except Exception as e:
                    st.error(f"Error publishing story: {str(e)}")
    else:        
        # Check if audio is available first
        audio_available = False
        try:
            if hasattr(story, 'audio') and story.audio and hasattr(story.audio, 'path') and story.audio.path:
                audio_available = os.path.exists(story.audio.path)
        except Exception:
            audio_available = False
            
        if st.button("🎬 Generate Video", type="primary"):
            try:
                with st.spinner("Generating video... This may take several minutes."):
                    video_file = story.get_video()
                    
                if video_file and os.path.exists(video_file):
                    st.success("Video generated successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Failed to generate video file.")
                    
            except VideoGenerationException as e:
                st.error(f"Video generation failed: {str(e)}")
            except Exception as e:
                st.error(f"Unexpected error during video generation: {str(e)}")
                
        # Show regenerate option if video exists but might be corrupted
        if current_video_file and not video_exists:
            st.warning(f"Video file was expected at {current_video_file} but not found.")
            if st.button("🔄 Regenerate Video"):
                try:
                    with st.spinner("Regenerating video..."):
                        video_file = story.get_video()
                        
                    if video_file and os.path.exists(video_file):
                        st.success("Video regenerated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to regenerate video file.")
                        
                except VideoGenerationException as e:
                    st.error(f"Video regeneration failed: {str(e)}")
                except Exception as e:
                    st.error(f"Unexpected error during video regeneration: {str(e)}")
else:
    st.title("🎥 Video Generation")
    st.warning("No story found. Please go to the Home page and fetch a story first.")
    if st.button("🏠 Go to Home"):
        st.switch_page("1_🏠_Home.py")

