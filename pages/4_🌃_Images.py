import streamlit as st
import os
import glob

from story.Audio import Audio
from story.Video import Video
from exceptions import AudioGenerationException

from gtts import gTTS
from gtts.tokenizer.pre_processors import abbreviations, end_of_line
import os, pyttsx3, re
import streamlit as st

from utils.conclusion import conclusion
from utils.introduction import introduction

def display_images_in_columns(images_data, use_story_objects=True):
    icol1, icol2, icol3, icol4 = st.columns([1, 1, 1, 1])
    
    for img in range(0, len(images_data), 4):
        with icol1:
            if img < len(images_data):
                if use_story_objects:
                    if hasattr(images_data[img], 'path') and images_data[img].path:
                        st.image(images_data[img].path, caption=images_data[img].title, width=200)
                else:
                    img_name = os.path.splitext(os.path.basename(images_data[img]))[0]
                    st.image(images_data[img], caption=img_name, width=200)
        with icol2:
            if img+1 < len(images_data):
                if use_story_objects:
                    if hasattr(images_data[img+1], 'path') and images_data[img+1].path:
                        st.image(images_data[img+1].path, caption=images_data[img+1].title, width=200)
                else:
                    img_name = os.path.splitext(os.path.basename(images_data[img+1]))[0]
                    st.image(images_data[img+1], caption=img_name, width=200)
        with icol3:
            if img+2 < len(images_data):
                if use_story_objects:
                    if hasattr(images_data[img+2], 'path') and images_data[img+2].path:
                        st.image(images_data[img+2].path, caption=images_data[img+2].title, width=200)
                else:
                    img_name = os.path.splitext(os.path.basename(images_data[img+2]))[0]
                    st.image(images_data[img+2], caption=img_name, width=200)
        with icol4:
            if img+3 < len(images_data):
                if use_story_objects:
                    if hasattr(images_data[img+3], 'path') and images_data[img+3].path:
                        st.image(images_data[img+3].path, caption=images_data[img+3].title, width=200)
                else:
                    img_name = os.path.splitext(os.path.basename(images_data[img+3]))[0]
                    st.image(images_data[img+3], caption=img_name, width=200)

mainargs = st.session_state.get('mainargs', {})
mock_selected = mainargs.get('mock', False)
images_dir = "output/images"

st.title("Displaying images for sceneries...")

if st.session_state.get('story'):
    story = st.session_state.get('story', None)

    if hasattr(story, 'images') and story.images:
        if not mock_selected:
            display_images_in_columns(story.images)
        else:
            st.warning("Mock mode displays existing images if present in {outimgs} directory.".format(outimgs=images_dir))
            if os.path.exists(images_dir):
                image_extensions = ['*.png', '*.jpg', '*.jpeg']
                existing_images = []
                for extension in image_extensions:
                    existing_images.extend(glob.glob(os.path.join(images_dir, extension)))
                
                if existing_images:
                    display_images_in_columns(existing_images, use_story_objects=False)
    
    st.divider()  # Add a visual separator
    
    story_title = story.texts['Hindi'].title
    final_text = introduction.get("Hindi") + story.texts['Hindi'].content + conclusion.get("Hindi")

    options = ["- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - Select TTS Library - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -", "gtts", "pyttsx3"]
    lib_name = st.selectbox("", options, index=0)
    
    # Only proceed if a real option is selected
    if lib_name == options[0]:
        lib_name = None  # Set to None to prevent form submission
        submit_button_disabled = True
    else:
        submit_button_disabled = False
        
    if lib_name == "gtts":
        file_extension = ".mp3"
    elif lib_name == "pyttsx3":
        file_extension = ".wav"
        
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Generate Audio", disabled=submit_button_disabled, use_container_width=True):
            audio_file_name = re.sub(r'_+', '_', re.sub(r'[^\w\s\u0900-\u097F]', '_', story_title).replace(" ", "_")) + file_extension

            print("Audio file: {path}\nfinal text: {text}".format(path="./output/audios/" + audio_file_name, text=final_text))
        
            audio = Audio(file_path="./output/audios/", file_name=audio_file_name)
        
            audio_file_name = audio.generate(text=final_text, lib=lib_name)
            if audio_file_name:
                st.session_state.audio_generated = True
            else:
                st.session_state.audio_generated = False
    
    if st.session_state.get('audio_generated', False):
        st.divider()  # Add a visual separator

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Generate Video", disabled=not st.session_state.audio_generated, use_container_width=True):
                video_file_name = re.sub(r'_+', '_', re.sub(r'[^\w\s\u0900-\u097F]', '_', story_title).replace(" ", "_")) + ".mp4"

                print("Video file: {path}: ".format(path="./output/videos/" + video_file_name))

                video = Video(file_path="./output/videos/", file_name=video_file_name)
                
                video_file_name = video.generate(video_path="./output/videos/", file_name=video_file_name, image_paths=story.images)
else:
    st.warning("No story found. Please go to the Home page and fetch a story first.")