import getopt, re
from sys import argv
from os import getenv
import streamlit as st

# Project imports
from Story import Story
from StoryMock import StoryMock
from utils.conclusion import conclusion
from utils.introduction import introduction
from utils.publishers.IPublisher import Publishers
from utils.Utils import usage

def process_args(args: list):
    retvals = {
        'fb': 0,
        'ig': 0,
        'images': 0,
        'mock': False,
        'tw': 0,
        'url': None,
        'yt': 0
    }

    try:
        opts, args = getopt.getopt(args, "hfgi:mtu:y", ["help", "facebook", "instagram" "images=", "mock", "twitter" "url=", "youtube"])
    except getopt.GetoptError as err:
        print(err)
        exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage(2)
        elif opt in ("-f", "--facebook"):
            retvals['fb'] = Publishers.FACEBOOK
        elif opt in ("-g", "--instagram"):
            retvals['ig'] = Publishers.INSTAGRAM
        elif opt in ("-i", "--image"):
            retvals['images'] = arg
        elif opt in ("-m", "--mock"):
            retvals['mock'] = True
        elif opt in ("-t", "--twitter"):
            retvals['tw'] = Publishers.TWITTER
        elif opt in ("-u", "--url"):
            retvals['url'] = arg
        elif opt in ("-y", "--youtube"):
            retvals['yt'] = Publishers.YOUTUBE
        else:
            usage(4)

    return retvals

def main(progargs: dict):
    # Create Story object and initialize it with the program arguments
    if progargs.get('mock'):
        story = StoryMock(progargs)
    else:
        story = Story(progargs)

    # Get story from the website
    story.get_text()

    # Translate story text and title to English so as get visualization 
    # text for creating images in the next step
    story.translate()

    # return story.title.get("Hindi"), story.text.get("Hindi"), story.title.get("English"), story.text.get("English")

    # The visualization text we get in step above 
    # is used to get images for the story
    story.get_images()

    # The images we get in step above are used to
    # generate a video for the story
    story.get_video()

    # Get story audio
    story.get_audio('gTTS')

    # Publish the story now
    # story.publish()

if __name__ == "__main__":
    mainargs = None

    if len(argv) < 2:
        st.set_page_config(layout="wide")
        st.title("Story Teller")
        st.subheader("Stories for social media")

        tb_request, tb_story_h, tb_story_e, tb_sceneries, tb_images, tb_audio, tb_video = st.tabs(["Request", "Hindi Story", "English Story", "Sceneries", "Images", "Audio", "Video"])
        with tb_request:
            with st.form(key='request_form'):
                url = st.text_input(label='URL', help='Enter the URL of the story you want to generate', autocomplete='on')

                c_fb, c_ig, c_tw, c_yt, c_mk = st.columns([1, 1, 1, 1, 1])

                with c_fb:
                    cb_fb = st.checkbox(label='Facebook')
            
                with c_ig:
                    cb_ig = st.checkbox(label='Instagram')
                
                with c_tw:
                    cb_tw = st.checkbox(label='Twitter')
                
                with c_yt:
                    cb_yt = st.checkbox(label='YouTube')
                
                with c_mk:
                    cb_mk = st.checkbox(label='Mock', value=True)

                submit_button = st.form_submit_button(label='Submit')
                if submit_button:
                    mainargs = {'url': url
                                , 'fb': cb_fb
                                , 'ig': cb_ig
                                , 'tw': cb_tw
                                , 'yt': cb_yt
                                , 'mock': cb_mk
                            }

                    # Now that we have program arguments, create Story object
                    # TODO: Use factory pattern to create Story object
                    if cb_mk:
                        story = StoryMock(mainargs)
                    else:
                        story = Story(mainargs)

                    # Get story from url
                    story.get_text()
                    
                    with tb_story_h:
                        with st.form(key='hindi_story_form'):
                            st.subheader("हिन्दी कहानी")
                            st.text_area(label="भूमिका", height=120, value=re.sub(r'[^\S\n]+', ' ', introduction.get("Hindi")))
                            st.text_area(label="कहानी", height=320, value=re.sub(r'[^\S\n]+', ' ', story.title.get("Hindi") + "\n" + story.text.get("Hindi").strip()))
                            st.text_area(label="अन्त:भाग", height=80, value=re.sub(r'[^\S\n]+', ' ', conclusion.get("Hindi")))
                            submit_story_h = st.form_submit_button(label='Submit')
                            if submit_story_h:
                                st.markdown("Looks OK...Hindi")

                    # Translate story text and title to English
                    # This is to get visualization text for creating images
                    story.translate()

                    with tb_story_e:
                        with st.form(key='📖 hindi_story_form'):
                            st.subheader("English Story")
                            st.text_area(label="Introduction", height=120, value=re.sub(r'[^\S\n]+', ' ', introduction.get("English")))
                            st.text_area(label="Story", height=300, value=re.sub(r'[^\S\n]+', ' ', story.title.get("English") + "\n" + story.text.get("English") if story.title.get("English") else story.text.get("English")))
                            st.text_area(label="Conclusion", height=80, value=re.sub(r'[^\S\n]+', ' ', conclusion.get("English")))
                            submit_story_e = st.form_submit_button(label='Submit')
                            if submit_story_e:
                                st.markdown("Looks OK...English")

                    # Get sceneries from translated story text
                    story.get_sceneries()

                    with tb_sceneries:
                        st.subheader("Scenery Titles and Explainations")
                        for key in story.sceneries:
                            st.text_area(label=key, height=80, value=re.sub(r'[^\S\n]+', ' ', story.sceneries.get(key).get("description")))

                    # Get images for the story using the visualization text
                    story.get_images()

                    with tb_images:
                        icol1, icol2, icol3, icol4 = st.columns([1, 1, 1, 1])

                        sceneries = list()
                        for key, value in story.sceneries.items():
                            tuple_elem = (key, value.get("path"))
                            sceneries.append(tuple_elem)
                        
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

                    # Get audio for the story
                    audio_file = story.get_audio('gTTS')

                    with tb_audio:
                        st.subheader("Audio")
                        st.audio(audio_file, format="audio/wav", start_time=0)
                    
                    # Get video for the story
                    video_file = story.get_video()

                    with tb_video:
                        st.subheader("Video")
                        st.video(video_file, format="video/mp4", start_time=0)
                    
                    # Publish the story
                    # story.publish()
    elif len(argv) == 2 and (argv[1] == '-h' or argv[1] == '--help'):
        usage(2)
    else:
        mainargs = process_args(argv[1:])
        h_title, h_text, e_title, e_text = main(mainargs)

        print(introduction.get("Hindi"), "\n\n")
        print(h_title, "\n\n")
        print(h_text, "\n\n")
        print(conclusion.get("Hindi"), "\n\n")

        print(introduction.get("English"), "\n\n")
        print(e_title, "\n\n")
        print(e_text, "\n\n")
        print(conclusion.get("English"), "\n\n")
