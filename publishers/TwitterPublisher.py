from langchain.chains.summarize import load_summarize_chain
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
import openai
import tweepy
from openai import OpenAI

# Project imports
from publishers.IPublisher import IPublisher

class TwitterPublisher(IPublisher):
    def __init__(self, credentials: dict) -> None:
        super().__init__(credentials)
        
    def login(self):
        pass

    def build(self, text: str, link: str):
        tweet = None
        docs = None
        llm = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=getenv('OPENROUTER_API_KEY'))

        template_prompt = """
        {text}

        Please suggest in single line what does above text do. {link} must be included in response.
        The response must be catchy, engaging, suitable for a tweet and in first person.
        Please sparingly use phrase 'Dive into the', instead use similar catchy and appealing phrases.
        """

        prompt_template = PromptTemplate(
            template=template_prompt
            , input_variables=['text', 'link']
        )

        tweet_prompt = prompt_template.format(text=text, link=link)
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=10
        )

        # we split the data into multiple chunks
        try:
            docs = text_splitter.create_documents([text, link])
            combine_chain = load_summarize_chain(
                llm=llm, 
                chain_type='stuff'
            )
            tweet = combine_chain.run(docs)
        except Exception as e:
            print("Exception Occurred: ", e)
            exit(2)

        print(tweet.strip())

        return tweet
    
    def publish(self, content):
        message = content.message
        image = content.image

        self._tweet(message)
        self._tweet_with_image(message=message, image=image) if content.publish_image else None

    def _tweet(self, message):
        self.api.update_status(message)

    def _tweet_with_image(self, message, image):
        self.api.update_with_media(image, message)
    
    def logout(self):
        pass