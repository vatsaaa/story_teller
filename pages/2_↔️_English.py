import re
import streamlit as st

from utils.conclusion import conclusion
from utils.introduction import introduction
from utils.Utils import MULTISPACE
from exceptions import StoryProcessingException

st.title("Story translated in English")

if st.session_state.get('story'):
    story = st.session_state.get('story', None)

    english_text = story.texts.get("English")
    if english_text and english_text.content:
        with st.form(key='english_story_form'):
            st.text_area(label="Introduction", height=120, value=re.sub(MULTISPACE, ' ', introduction.get("English")))
            
            # Safe handling of potentially None values for English text
            if english_text.title:
                english_story_content = english_text.title.strip() + "\n" + english_text.content.strip()
            else:
                english_story_content = english_text.content.strip()
            
            st.text_area(label="Story", height=300, value=re.sub(MULTISPACE, ' ', english_story_content))
            st.text_area(label="Conclusion", height=80, value=re.sub(MULTISPACE, ' ', conclusion.get("English")))

            submit_story_e = st.form_submit_button(label='Get sceneries', help='Click to extract sceneries from the story text')
            if submit_story_e:
                try:
                    story.get_sceneries()
                    st.session_state['story'] = story
                    st.success("Sceneries extracted successfully!")
                except StoryProcessingException as e:
                    st.error("🎭 **Failed to get sceneries from the story text**")
                    st.warning(f"Error details: {str(e)}")
                    st.info("Please check your story content and try again.")
                except Exception as e:
                    st.error(f"❌ **Unexpected Error**: {str(e)}. Please try again.")
