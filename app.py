import getopt
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
        'tw': 0,
        'url': None,
        'yt': 0
    }

    try:
        opts, args = getopt.getopt(args, "hi:u:", ["help", "images=", "url="])
    except getopt.GetoptError as err:
        print(err)
        exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage(2)
        elif opt in ("-f", "--facebook"):
            retvals['fb'] = SocialMedia.FACEBOOK
        elif opt in ("-g", "--gram"):
            retvals['ig'] = SocialMedia.INSTAGRAM
        elif opt in ("-i", "--image"):
            retvals['images'] = arg
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

    return story.title, story.text

    # Translate story text and title to English so as get visualization 
    # text for creating images in the next step
    # story.translate()

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
    # st.title("Story Generator")
    # st.subheader("A tool to generate stories for social media")

    # with st.form(key='my_form'):
    #     # st.write("Enter the URL of the story you want to generate")
    #     url = st.text_input(label='URL', help='Enter the URL of the story you want to generate', autocomplete='on')

    #     cb_fb = st.checkbox(label='Facebook')
    #     cb_ig = st.checkbox(label='Instagram')
    #     cb_tw = st.checkbox(label='Twitter')
    #     cb_yt = st.checkbox(label='YouTube')
        
    #     submit_button = st.form_submit_button(label='Submit')

    # if submit_button:
    #     title, text = main({'url': url,
    #                         'fb': cb_fb,
    #                         'ig': cb_ig, 
    #                         'tw': cb_tw, 
    #                         'yt': cb_yt
    #                         })
    #     st.balloons()
    #     st.write(title.get("Hindi") + "\n\n" + text.get("Hindi"))
        # st.success('Story generated successfully!')

    main(process_args(argv[1:]))