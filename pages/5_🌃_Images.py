import re
import streamlit as st

st.title("Images for each scenery...")

if st.session_state.get('story'):
    story = st.session_state.get('story', None)

    print("Here 10")

    if story.sceneries:
        print("Here 11")
        sceneries = list()
        for key, value in story.sceneries.items():
            print("Key:", re.sub(' ', '', key), "Value: ", value.get("path"))
            tuple_elem = (key, value.get("path"))
            sceneries.append(tuple_elem)

        icol1, icol2, icol3, icol4 = st.columns([1, 1, 1, 1])
        for img in range(0, len(sceneries), 4):
            with icol1:
                if story.sceneries.get(key).get("path") and img < len(sceneries):
                    st.image(sceneries[img][1], caption=sceneries[img][0], width=200)
            with icol2:
                if story.sceneries.get(key).get("path") and img+1 < len(sceneries):
                    st.image(sceneries[img+1][1], caption=sceneries[img+1][0], width=200)

            with icol3:
                if story.sceneries.get(key).get("path") and img+2 < len(sceneries):
                    st.image(sceneries[img+2][1], caption=sceneries[img+2][0], width=200)

            with icol4:
                if story.sceneries.get(key).get("path") and img+3 < len(sceneries):
                    st.image(sceneries[img+3][1], caption=sceneries[img+3][0], width=200)

        # audio_file = story.get_audio('gTTS')