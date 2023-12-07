from instabot import Bot
from os import getenv

# Priject imports
from utils.publishers.IPublisher import IPublisher

class FacebookPublisher(IPublisher):
    def __init__(self, username: str=getenv('INSTAGRAM_USER_NAME'), password: str=getenv('INSTAGRAM_USER_PASS')) -> None:
        super().__init__()
        
        self.username = username
        self.password = password
    
    def login(self) -> None:
        pass
    
    def publish(self, content) -> None:
        image = content.get("image")
        caption = content.get("caption")

    def logout(self) -> None:
        pass    