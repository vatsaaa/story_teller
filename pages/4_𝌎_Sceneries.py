import json, re
import streamlit as st

from utils.Utils import MULTISPACE

st.title("Get Sceneries Description")

if st.session_state.get('story'):
    story = st.session_state.get('story', None)

    print("Here 1")

    if type(story.sceneries) is str:
        print("Here 2 i.e str")
        story.sceneries = json.loads(re.sub(MULTISPACE, ' ', story.sceneries))
    elif type(story.sceneries) is dict:
        print("Here 3 i.e dict")
        pass
    else:
        print("Here 3 i.e tottaly unexpected")
        st.error("Error: Please ensure sceneries are fetched properly!")

    if story.sceneries:
        print("Here 4 i.e story.sceneries is not None")
        with st.form(key='sceneries_form'):
            st.subheader("Scenery Titles and Explainations")

            for key in story.sceneries:
                st.text_area(label=key.strip(), height=80, value=story.sceneries.get(key).get('description'), key=key.strip())
                
            submit_sceneries = st.form_submit_button(label='Submit')
            if submit_sceneries:
                story.get_images()
                st.session_state['story'] = story
