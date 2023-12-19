import streamlit as st

from story.StoryFactory import StoryFactory

st.title("Create Video")

if st.session_state.get('story'):
    story = st.session_state.get('story', None)

    if story.video_file:
        with st.form(key='video_form'):
            video_file = story.get_video()

            st.audio(video_file, format="video/mp4", start_time=0)

            submit_video = st.form_submit_button(label='Submit')
            if submit_video:
                video_file = story.get_video()
                st.session_state['story'] = story

