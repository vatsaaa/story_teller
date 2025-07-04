import getopt, re
from sys import argv
from os import getenv
import streamlit as st

# Project imports
from exceptions import ConfigurationException, ImageGenerationException, TranslationException
from publishers.IPublisher import PublisherType
from publishers.PublisherFactory import PublisherFactory
from story.StoryFactory import StoryFactory
from utils.conclusion import conclusion
from utils.introduction import introduction
from utils.conclusion import conclusion
from utils.introduction import introduction
from utils.Utils import MULTISPACE, usage

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
    from publishers.IPublisher import PublisherType
    from exceptions import PublishingException, ConfigurationException
    from os import getenv
    
    publishers = list()
    
    # Map boolean flags to PublisherType enum values and their required credentials
    publisher_configs = {
        'fb': {
            'type': PublisherType.FACEBOOK,
            'params': lambda: {'page_id': getenv('FBIG_PAGE_ID')},
            'name': 'Facebook'
        },
        'ig': {
            'type': PublisherType.INSTAGRAM,
            'params': lambda: {'credentials': {'access_token': getenv('IG_ACCESS_TOKEN')}},
            'name': 'Instagram'
        },
        'tw': {
            'type': PublisherType.TWITTER,
            'params': lambda: {'credentials': {'access_token': getenv('TWITTER_ACCESS_TOKEN')}},
            'name': 'Twitter'
        },
        'yt': {
            'type': PublisherType.YOUTUBE,
            'params': lambda: {'credentials': {'access_token': getenv('YOUTUBE_ACCESS_TOKEN')}},
            'name': 'YouTube'
        }
    }
    
    for key, config in publisher_configs.items():
        # Only create publisher if the corresponding flag is True
        if progargs.get(key, False):
            try:
                params = config['params']()
                p = PublisherFactory.create_publisher(config['type'], **params)
                publishers.append(p)
                print(f"✓ {config['name']} publisher configured successfully")
            except (ValueError, PublishingException, ConfigurationException) as err:
                print(f"Warning: Failed to create {config['name']} publisher: {err}")
                continue

    if not publishers:
        print("Note: No publishers were configured. Story will be processed but not published.")
    
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
    except ConfigurationException as e:
        print(f"Warning: Image generation not configured: {str(e)}. Continuing without images...")
    except ImageGenerationException as e:
        print(f"Warning: Error generating images: {str(e)}. Continuing...")
    except Exception as e:
        print(f"Warning: Unexpected error during image generation: {str(e)}. Continuing...")

    # Get story audio
    story.get_audio('gTTS')

    # The images we get in step above are used to generate a video for the story
    story.get_video()

    # Publish the story now
    publishers = get_publishers(progargs)
    story.publish(publishers)

    return story.title.get("Hindi"), story.text.get("Hindi"), story.title.get("English"), story.text.get("English")

URL_PATTERN = r"^http://|^https://"
if __name__ == "__main__":
    mainargs = None

    if len(argv) < 2:
        st.set_page_config(layout="wide", page_title="Story Teller", page_icon="📖")
        st.title("Story Teller")
        st.subheader("Kids stories for social media")

        with st.form(key='request_form'):
            url = st.text_input(label='URL', help='Enter the URL of the story you want to generate', autocomplete='on')
            if url and not re.match(URL_PATTERN, url):
                st.error("Please give a valid URL to fetch the story from!")

            # Publisher selection with Mock exclusivity
            st.subheader("Select Publishers")
            
            c_fb, c_ig, c_tw, c_yt, c_mk = st.columns([1, 1, 1, 1, 1])

            with c_mk:
                cb_mk = st.checkbox(label='Mock', value=st.session_state.get('mock_mode', False))

            with c_fb:
                cb_fb = st.checkbox(label='Facebook')
        
            with c_ig:
                cb_ig = st.checkbox(label='Instagram')
            
            with c_tw:
                cb_tw = st.checkbox(label='Twitter')
            
            with c_yt:
                cb_yt = st.checkbox(label='YouTube')

            if 'mainargs' not in st.session_state:
                st.session_state['mainargs'] = None

            submit_button = st.form_submit_button(label='Get Hindi Story', help='Click to fetch the story from the given URL')
            if submit_button:
                mainargs = {'url': url
                            , 'fb': cb_fb
                            , 'ig': cb_ig
                            , 'tw': cb_tw
                            , 'yt': cb_yt
                            , 'mock': cb_mk
                        }

                st.session_state['mainargs'] = mainargs

                # Now that we have program arguments, create Story object
                story = StoryFactory.create_story(progargs=mainargs)

                # Set story object in session state
                st.session_state['story'] = story

                # Get story tedxt from the given URL
                story.get_text()

        # Show the story content outside the form if story is loaded
        if 'story' in st.session_state and st.session_state['story'] is not None:
            st.divider()
            
            story = st.session_state['story']
            
            # Safe handling of potentially None values
            hindi_text = story.texts.get("Hindi")
            if hindi_text and hindi_text.title and hindi_text.content:
                story_content = hindi_text.title.strip() + "\n" + hindi_text.content.strip()
            else:
                story_content = "Story not loaded yet. Please provide a valid URL."
            
            # Create a separate form for translation
            with st.form(key='translation_form'):
                # Show the story
                st.text_area(label="भूमिका", height=120, value=re.sub(MULTISPACE, ' ', introduction.get("Hindi")))                
                st.text_area(label="कहानी", height=320, value=re.sub(MULTISPACE, ' ', story_content))
                st.text_area(label="अन्त:भाग", height=80, value=re.sub(MULTISPACE, ' ', conclusion.get("Hindi")))

                submit_story_h = st.form_submit_button(label='Translate Story to English')
                if submit_story_h:
                    try:
                        story.translate()
                        st.session_state['story'] = story
                        st.success("Story translated to English successfully!")
                    except TranslationException as e:
                        st.error("🌐 ** Failed to translate story to English**")
                        st.warning(f"Error details: {str(e)}")
                        st.info("Please check that the Hindi story content is loaded properly and try again.")
                    except Exception as e:
                        st.error(f"❌ **Unexpected Error**: {str(e)}")
                        st.info("Please try again.")
    elif len(argv) == 2 and (argv[1] == '-h' or argv[1] == '--help'):
        usage(2)
    else:
        mainargs = process_args(argv[1:])
        h_title, h_text, e_title, e_text = main(mainargs)