from instabot import Bot
from os import getenv

# Priject imports
from utils.IPublisher import IPublisher

class InstagramPublisher(IPublisher):
    def __init__(self, username: str=getenv('INSTAGRAM_USER_NAME'), password: str=getenv('INSTAGRAM_USER_PASS')) -> None:
        super().__init__()
        
        self.username = username
        self.password = password

        self.bot = Bot()
    
    def login(self) -> None:
        self.bot.login(username=self.username, password=self.password)
    
    def publish(self, content) -> None:
        image = content.get("image")
        caption = content.get("caption")

        self.bot.upload_photo(image, caption=caption)

    def logout(self) -> None:
        self.bot.logout()
    