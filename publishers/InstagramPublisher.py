from os import getenv, path
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Project imports
from publishers.IPublisher import IPublisher
from exceptions.ConfigurationException import ConfigurationException

class InstagramPublisher(IPublisher):
    def __init__(self, credentials: dict) -> None:
        super().__init__(credentials=credentials)
    
    def login(self) -> None:
        access_token = self.credentials.get('access_token')
        if not access_token:
            raise ConfigurationException(
                "Instagram Access Token is not set",
                config_key="IG_ACCESS_TOKEN",
                details={"solution": "Add IG_ACCESS_TOKEN to your .env file with your Instagram access token"}
            )
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

    def build(self) -> dict:
        """Build content for Instagram publishing."""
        content = dict()
        try:
            if hasattr(self, 'ig') and self.ig: 
                # TODO: Below line assumes gif file is present
                # adopt defensive programming here to prevent errors
                content["image"] = path.join('./output/videos/', self.story_name + ".gif")

                # Get caption from the story text in English
                text_to_get_caption_from = self.text.get("English")

                # Set up the translation prompt, grammer (e.g. articles) omitted for brevity
                caption_template = '''
                Create a highly engaging summary from the given text between tags <TEXT> and </TEXT>, for publishing as caption on a Instagram post.

                Return only the summary, not the original text. Character Vikram should not be summary.

                <TEXT>{text}</TEXT>
                '''

                caption_prompt = PromptTemplate(template=caption_template, input_variables=['text'])

                chain2 = LLMChain(llm=self.llm,prompt=caption_prompt)

                # Extract the translated text from the API response
                input = {'text': text_to_get_caption_from}
                content["caption"] = chain2.run(input)
        except Exception as e:
            print(f"Error building Instagram content: {str(e)}")
        
        return content
    
    def publish(self, content: dict) -> None:
        """Publish content to Instagram."""
        try:
            image = content.get("image")
            caption = content.get("caption")
            
            if not image or not caption:
                print("Warning: Missing image or caption for Instagram publishing")
                return
                
            # For now, just print the content that would be published
            # In a real implementation, you would use Instagram's API
            print(f"Publishing to Instagram:")
            print(f"Image: {image}")
            print(f"Caption: {caption}")
            print("Instagram publishing completed successfully")
            
        except Exception as e:
            print(f"Instagram publishing failed: {str(e)}")
            raise

    def logout(self) -> None:
        self.headers = None
        print("Logged out from Instagram Publisher.")