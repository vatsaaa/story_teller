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
    story.get_images()

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
        st.set_page_config(layout="wide", page_title="Story Teller", page_icon="📖")
        st.title("Story Teller")
        st.subheader("Stories for social media")

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
                cb_mk = st.checkbox(label='Mock')

            if 'mainargs' not in st.session_state:
                st.session_state['mainargs'] = None

            submit_button = st.form_submit_button(label='Submit')
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

                # Get story from user given url
                pattern = r"^http://|^https://"
                try:
                     if url and re.match(pattern, url):
                         story.get_text()
                except Exception as e:
                    st.error("Please give a valid URL to fetch the story from!")

                # Set story object in session state
                st.session_state['story'] = story
                    
                # Publish the story
                # publishers = get_publishers(mainargs)
                # story.publish(publishers=publishers)
    elif len(argv) == 2 and (argv[1] == '-h' or argv[1] == '--help'):
        usage(2)
    else:
        mainargs = process_args(argv[1:])
        h_title, h_text, e_title, e_text = main(mainargs)

        print("भूमिका: ", introduction.get("Hindi"), "\n\n")
        print("शीर्षक: ", h_title, "\n\n")
        print("कहानी: ", h_text, "\n\n")
        print("उपसंहार: ", conclusion.get("Hindi"), "\n\n")

        print("Introduction: ", introduction.get("English"), "\n\n")
        print("Title: ", e_title, "\n\n")
        print("Story: ", e_text, "\n\n")
        print("Conclusion: ", conclusion.get("English"), "\n\n")
