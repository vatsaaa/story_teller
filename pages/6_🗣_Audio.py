import streamlit as st

if st.session_state.get('story'):
    story = st.session_state.get('story', None)
    audio_file = story.get_audio('gTTS')

    if audio_file:
        st.title("Generating story audio...")
        with st.form(key='audio_form'):
            st.audio(audio_file, format="audio/wav", start_time=0)

            submit_audio = st.form_submit_button(label='Submit')
            if submit_audio:
                video_file = story.get_video()
                st.session_state['story'] = story
    else:
        st.title("Generating story audio...")
