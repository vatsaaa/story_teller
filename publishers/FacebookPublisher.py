from instabot import Bot
from os import getenv

# Priject imports
from publishers.IPublisher import IPublisher

class FacebookPublisher(IPublisher):
    def __init__(self, credentials: dict) -> None:
        super().__init__(credentials=credentials)
    
    def login(self) -> None:
        pass
    
    def publish(self, content) -> None:
        image = content.get("image")
        caption = content.get("caption")

    def logout(self) -> None:
        pass    