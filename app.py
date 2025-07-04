import getopt, re
from sys import argv
from os import getenv
import streamlit as st

# Project imports
from story.StoryFactory import StoryFactory
from utils.conclusion import conclusion
from utils.introduction import introduction
from publishers.IPublisher import PublisherType
from publishers.PublisherFactory import PublisherFactory
from utils.Utils import usage, MULTISPACE

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
            retvals['fb'] = PublisherType.FACEBOOK
        elif opt in ("-g", "--instagram"):
            retvals['ig'] = PublisherType.INSTAGRAM
        elif opt in ("-i", "--image"):
            retvals['images'] = arg
        elif opt in ("-m", "--mock"):
            retvals['mock'] = True
        elif opt in ("-t", "--twitter"):
            retvals['tw'] = PublisherType.TWITTER
        elif opt in ("-u", "--url"):
            retvals['url'] = arg
        elif opt in ("-y", "--youtube"):
            retvals['yt'] = PublisherType.YOUTUBE
        else:
            usage(4)

    return retvals

def get_publishers(progargs: dict):
    publisters_type = list()
    publisters_type.append(progargs.get('fb'))
    publisters_type.append(progargs.get('ig'))
    publisters_type.append(progargs.get('tw'))
    publisters_type.append(progargs.get('yt'))
    
    publishers = list()
    for pt in publisters_type:
        try:
            p = PublisherFactory.create_publisher(pt)
        except ValueError as err:
            print(err)
            continue
        
        publishers.append(p)

    return publishers

def main(progargs: dict):
    # Create Story object and initialize it with the program arguments
    story = StoryFactory.create_story(progargs)

    # Get story from the website
    story.get_text()

    # Translate story text and title to English so as get visualization 
    # text for creating images in the next step
    story.translate()

    # The visualization text we get in step above 
    # is used to get images for the story
    try:
        story.get_images()
    except Exception as e:
        if "TEXT_TO_IMAGE_URL is not set" in str(e) or "Image generation is not configured" in str(e):
            print("Warning: Image generation not configured. Continuing without images...")
        else:
            print(f"Warning: Error generating images: {str(e)}. Continuing...")

    # Get story audio
    story.get_audio('gTTS')

    # The images we get in step above are used to
    # generate a video for the story
    story.get_video()

    # Publish the story now
    publishers = get_publishers(progargs)
    story.publish(publishers)

    return story.title.get("Hindi"), story.text.get("Hindi"), story.title.get("English"), story.text.get("English")

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

                # Publisher selection with Mock exclusivity
                st.subheader("Select Publishers")
                
                # Initialize mock state if it doesn't exist
                if 'app_mock_mode' not in st.session_state:
                    st.session_state['app_mock_mode'] = False
                
                c_fb, c_ig, c_tw, c_yt, c_mk = st.columns([1, 1, 1, 1, 1])

                # Mock checkbox - always enabled
                with c_mk:
                    cb_mk = st.checkbox(label='Mock', value=st.session_state.get('app_mock_mode', False))

                # Other checkboxes - disabled when mock is enabled
                mock_disabled = st.session_state.get('app_mock_mode', False)
                
                with c_fb:
                    if mock_disabled:
                        st.checkbox(label='Facebook', value=False, disabled=True)
                        cb_fb = False
                    else:
                        cb_fb = st.checkbox(label='Facebook')
            
                with c_ig:
                    if mock_disabled:
                        st.checkbox(label='Instagram', value=False, disabled=True)
                        cb_ig = False
                    else:
                        cb_ig = st.checkbox(label='Instagram')
                
                with c_tw:
                    if mock_disabled:
                        st.checkbox(label='Twitter', value=False, disabled=True)
                        cb_tw = False
                    else:
                        cb_tw = st.checkbox(label='Twitter')
                
                with c_yt:
                    if mock_disabled:
                        st.checkbox(label='YouTube', value=False, disabled=True)
                        cb_yt = False
                    else:
                        cb_yt = st.checkbox(label='YouTube')

                # Show info message when Mock is selected
                if st.session_state.get('app_mock_mode', False):
                    st.info("ℹ️ **Mock Publisher Selected**: All other publishers are disabled. Uncheck Mock to enable other publishers.")

                # Handle mock mode toggle outside the form
                if cb_mk != st.session_state.get('app_mock_mode', False):
                    st.session_state['app_mock_mode'] = cb_mk
                    if cb_mk:
                        st.warning("🔄 **Mock mode enabled** - Page will refresh to disable other publishers.")
                        st.rerun()
                    else:
                        st.success("🔄 **Mock mode disabled** - Page will refresh to enable other publishers.")
                        st.rerun()

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
                    story = StoryFactory.create_story(progargs=mainargs)

                    # Get story from user given url
                    pattern = r"^http://|^https://"
                    story_fetched = False
                    try:
                         if url and re.match(pattern, url):
                             story.get_text()
                             story_fetched = True
                    except Exception as e:
                        st.error("Please give a valid URL to fetch the story from!")
                    
                    with tb_story_h:
                        with st.form(key='hindi_story_form'):
                            st.subheader("हिन्दी कहानी")
                            st.text_area(label="भूमिका", height=120, value=re.sub(MULTISPACE, ' ', introduction.get("Hindi")))
                            
                            # Safe handling of potentially None values
                            hindi_text = story.texts.get("Hindi")
                            if hindi_text and hindi_text.title and hindi_text.content:
                                story_content = hindi_text.title.strip() + "\n" + hindi_text.content.strip()
                            else:
                                story_content = "Story not loaded yet. Please provide a valid URL."
                            
                            st.text_area(label="कहानी", height=320, value=re.sub(MULTISPACE, ' ', story_content))
                            st.text_area(label="अन्त:भाग", height=80, value=re.sub(MULTISPACE, ' ', conclusion.get("Hindi")))
                            submit_story_h = st.form_submit_button(label='Submit')
                            if submit_story_h:
                                st.markdown("Looks OK...Hindi")

                    # Translate story text and title to English only if story was fetched
                    # This is to get visualization text for creating images
                    if story_fetched:
                        story.translate()

                    with tb_story_e:
                        with st.form(key='english_story_form'):
                            st.subheader("English Story")
                            st.text_area(label="Introduction", height=120, value=re.sub(MULTISPACE, ' ', introduction.get("English")))
                            
                            # Safe handling of potentially None values for English text
                            english_text = story.texts.get("English")
                            if english_text and english_text.content:
                                if english_text.title:
                                    english_story_content = english_text.title.strip() + "\n" + english_text.content.strip()
                                else:
                                    english_story_content = english_text.content.strip()
                            else:
                                english_story_content = "English translation not available yet. Please translate the story first."
                            
                            st.text_area(label="Story", height=300, value=re.sub(MULTISPACE, ' ', english_story_content))
                            st.text_area(label="Conclusion", height=80, value=re.sub(MULTISPACE, ' ', conclusion.get("English")))
                            submit_story_e = st.form_submit_button(label='Submit')
                            if submit_story_e:
                                st.markdown("Looks OK...English")

                    # Get sceneries from translated story text
                    story.get_sceneries()

                    with tb_sceneries:
                        with st.form(key='sceneries_form'):
                            st.subheader("Scenery Titles and Explainations")
                            for image in story.images:
                                st.text_area(label=image.title, height=80, value=re.sub(MULTISPACE, ' ', image.description))
                            submit_sceneries = st.form_submit_button(label='Submit')
                            if submit_story_h:
                                st.markdown("Looks OK...Sceneries")

                    # Get images for the story using the visualization text
                    try:
                        story.get_images()
                    except Exception as e:
                        if "TEXT_TO_IMAGE_URL is not set" in str(e) or "Image generation is not configured" in str(e):
                            st.warning("⚠️ Image generation not configured. Add TEXT_TO_IMAGE_URL to .env file to generate images.")
                        else:
                            st.warning(f"Error generating images: {str(e)}")

                    with tb_images:
                        icol1, icol2, icol3, icol4 = st.columns([1, 1, 1, 1])

                        # Check if images have been generated
                        if hasattr(story, 'images') and story.images:
                            for img in range(0, len(story.images), 4):
                                with icol1:
                                    if img < len(story.images) and hasattr(story.images[img], 'path') and story.images[img].path:
                                        st.image(story.images[img].path, caption=story.images[img].title, width=200)
                                with icol2:
                                    if img+1 < len(story.images) and hasattr(story.images[img+1], 'path') and story.images[img+1].path:
                                        st.image(story.images[img+1].path, caption=story.images[img+1].title, width=200)
                                with icol3:
                                    if img+2 < len(story.images) and hasattr(story.images[img+2], 'path') and story.images[img+2].path:
                                        st.image(story.images[img+2].path, caption=story.images[img+2].title, width=200)
                                with icol4:
                                    if img+3 < len(story.images) and hasattr(story.images[img+3], 'path') and story.images[img+3].path:
                                        st.image(story.images[img+3].path, caption=story.images[img+3].title, width=200)
                        else:
                            st.info("Images will be generated after sceneries are created.")

                    # Get audio for the story
                    audio_file = story.get_audio('gTTS')

                    with tb_audio:
                        with st.form(key='audio_form'):
                            st.subheader("Audio")
                            # st.audio(audio_file, format="audio/wav", start_time=0)
                            submit_audio = st.form_submit_button(label='Submit')
                            if submit_audio:
                                st.markdown("Looks OK...Audio")
                    
                    # Get video for the story
                    video_file = story.get_video()

                    with tb_video:
                        with st.form(key='video_form'):
                            st.subheader("Video")
                            # st.video(video_file, format="video/mp4", start_time=0)
                            submit_video = st.form_submit_button(label='Submit')
                            if submit_video:
                                st.markdown("Looks OK...Video")
                    
                    # Publish the story
                    publishers = get_publishers(mainargs)
                    story.publish(publishers=publishers)
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
