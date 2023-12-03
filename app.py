import getopt, re
from sys import argv
from os import getenv
import streamlit as st

# Project imports
from Story import Story
from utils.Constants import SocialMedia
from utils.conclusion import conclusion
from utils.introduction import introduction

def usage(exit_code: int) -> None:
    print("Usage: app.py [OPTIONS]")
    print("Options:")
    print("\t-h, --help\t\t\t\tPrint this help message\n\n")
    print("\t- f, --help\t\t\t\tPublish to Facebook")
    print("\t- g, --help\t\t\t\tPublish to Instagram")
    print("\t-i, --image\t\t\t\tNumber of images to generate")
    print("\t-t, --help\t\t\t\tPublish to Twitter (i.e. x.com)")
    print("\t-u, --url\t\t\t\tUrl to get story from")
    print("\t-y, --help\t\t\t\tPublish to YouTube")
    exit(exit_code)

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
            retvals['fb'] = SocialMedia.FACEBOOK
        elif opt in ("-g", "--instagram"):
            retvals['ig'] = SocialMedia.INSTAGRAM
        elif opt in ("-i", "--image"):
            retvals['images'] = arg
        elif opt in ("-m", "--mock"):
            retvals['mock'] = True
        elif opt in ("-t", "--twitter"):
            retvals['tw'] = SocialMedia.TWITTER
        elif opt in ("-u", "--url"):
            retvals['url'] = arg
        elif opt in ("-y", "--youtube"):
            retvals['yt'] = SocialMedia.YOUTUBE
        else:
            usage(4)

    return retvals

def main(progargs: dict):
    # Create Story object and initialize it with the program arguments
    story = Story(progargs)

    # Get story from the website
    story.get_text()

    # Translate story text and title to English so as get visualization 
    # text for creating images in the next step
    story.translate()

    # return story.title.get("Hindi"), story.text.get("Hindi"), story.title.get("English"), story.text.get("English")

    # The visualization text we get in step above 
    # is used to get images for the story
    # story.get_images()

    # The images we get in step above are used to
    # generate a video for the story
    # story.get_video()

    # Get story audio
    # story.get_audio('gTTS')

    # Publish the story now
    # story.publish()

if __name__ == "__main__":
    mainargs = None

    if len(argv) < 2:
        st.set_page_config(layout="wide")
        st.title("Story Teller")
        st.subheader("Stories for social media")

        with st.form(key='my_form'):
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
                story = Story(mainargs)

                # Get story from url
                story.get_text()
                
                st.subheader("हिन्दी कहानी")
                st.text_area(label="भूमिका", height=120, value=re.sub(r'[^\S\n]+', ' ', introduction.get("Hindi")))
                st.text_area(label="कहानी", height=320, value=re.sub(r'[^\S\n]+', ' ', story.title.get("Hindi") + "\n" + story.text.get("Hindi").strip()))
                st.text_area(label="अन्त:भाग", height=80, value=re.sub(r'[^\S\n]+', ' ', conclusion.get("Hindi")))

                st.markdown("""<hr style="height:2px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

                # Translate story text and title to English
                # This is to get visualization text for creating images
                story.translate()
                st.subheader("English Story")
                st.text_area(label="Introduction", height=120, value=re.sub(r'[^\S\n]+', ' ', introduction.get("English")))
                st.text_area(label="Story", height=300, value=re.sub(r'[^\S\n]+', ' ', story.title.get("English") + "\n" + story.text.get("English") if story.title.get("English") else story.text.get("English")))
                st.text_area(label="Conclusion", height=80, value=re.sub(r'[^\S\n]+', ' ', conclusion.get("English")))

                # Get sceneries from translated story text
                story.get_sceneries()
                st.subheader("Extracted Sceneries")
                for key in story.sceneries:
                    st.text_area(label=key, height=80, value=re.sub(r'[^\S\n]+', ' ', story.sceneries.get(key).get("description")))

                # Get images for the story using the visualization text
                # story.get_images()

                # Get audio for the story
                # story.get_audio('gTTS')

                # Get video for the story
                # story.get_video()

                # Publish the story
                story.publish()
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
