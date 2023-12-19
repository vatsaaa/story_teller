import re
import streamlit as st

from utils.conclusion import conclusion
from utils.introduction import introduction
from utils.Utils import MULTISPACE

st.title("Translate story to English")

if st.session_state.get('story'):
    story = st.session_state.get('story', None)

    if story.text.get("English", None):
        with st.form(key='english_story_form'):
            st.text_area(label="Introduction", height=120, value=re.sub(MULTISPACE, ' ', introduction.get("English")))
            st.text_area(label="Story", height=300, value=re.sub(MULTISPACE, ' ', story.title.get("English") + "\n" + story.text.get("English") if story.title.get("English") else story.text.get("English")))
            st.text_area(label="Conclusion", height=80, value=re.sub(MULTISPACE, ' ', conclusion.get("English")))

            submit_story_e = st.form_submit_button(label='Submit')
            if submit_story_e:
                story.get_sceneries()
                print("Sceneries: ", story.sceneries, "Type: ", type(story.sceneries))
                st.session_state['story'] = story
