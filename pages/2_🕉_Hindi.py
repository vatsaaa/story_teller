import re
import streamlit as st

from utils.conclusion import conclusion
from utils.introduction import introduction
from utils.Utils import MULTISPACE

st.title("Get Hindi Story")

if st.session_state.get('mainargs') and st.session_state.get('story'):
    story = st.session_state.get('story', None)

    if story:
        with st.form(key='hindi_story_form'):
            st.text_area(label="भूमिका", height=120, value=re.sub(MULTISPACE, ' ', introduction.get("Hindi")))
            st.text_area(label="कहानी", height=320, value=re.sub(MULTISPACE, ' ', story.title.get("Hindi") + "\n" + story.text.get("Hindi").strip()))
            st.text_area(label="अन्त:भाग", height=80, value=re.sub(MULTISPACE, ' ', conclusion.get("Hindi")))

            submit_story_h = st.form_submit_button(label='Submit')
            if submit_story_h:
                story.translate()
                st.session_state['story'] = story