from dotenv import load_dotenv
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
from os import getenv

load_dotenv()

# Project imports
from publishers.IPublisher import IPublisher
from exceptions.ConfigurationException import ConfigurationException

class TwitterPublisher(IPublisher):
    def __init__(self, credentials: dict) -> None:
        super().__init__(credentials)
        
    def login(self):
        """Login to Twitter with credential validation."""
        access_token = self.credentials.get('access_token')
        if not access_token:
            raise ConfigurationException(
                "Twitter Access Token is not set",
                config_key="TWITTER_ACCESS_TOKEN",
                details={"solution": "Add TWITTER_ACCESS_TOKEN to your .env file with your Twitter access token"}
            )

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
    
    def publish(self, content: dict):
        """Publish content to Twitter."""
        try:
            # Extract text content for tweet
            text_content = content.get("text", {})
            hindi_text = text_content.get("hindi", "")
            english_text = text_content.get("english", "")
            title = text_content.get("title", "Story")
            
            # Use English text for tweet, fallback to Hindi if English not available
            message_text = english_text if english_text else hindi_text
            
            if not message_text:
                print("Warning: No text content available for Twitter publishing")
                return
            
            # Build tweet using the existing build method
            # For now, we'll use a simple approach since we don't have a link
            tweet_message = f"{title}: {message_text[:200]}..." if len(message_text) > 200 else f"{title}: {message_text}"
            
            # Get image if available
            images = content.get("images", [])
            first_image = images[0] if images else None
            
            # Publish tweet
            self._tweet(tweet_message)
            
            # If image available, publish with image
            if first_image:
                self._tweet_with_image(message=tweet_message, image=first_image)
                
            print("Twitter publishing completed successfully")
            
        except Exception as e:
            print(f"Twitter publishing failed: {str(e)}")
            raise

    def _tweet(self, message):
        """Mock tweet function - in real implementation would use Twitter API."""
        print(f"Tweeting: {message}")

    def _tweet_with_image(self, message, image):
        """Mock tweet with image function - in real implementation would use Twitter API."""
        print(f"Tweeting with image: {message}, Image: {image}")
    
    def logout(self):
        pass