from os import getenv

# Priject imports
from publishers.IPublisher import IPublisher

class FacebookPublisher(IPublisher):
    def __init__(self, page_id: str) -> None:
        super().__init__()
        self.base_url = getenv('FBIG_BASE_URL') + getenv('FBIG_BASE_VER') + '{}/photos'
        self.base_url = self.base_url.format(page_id)
    
    def login(self) -> None:
        pass
    
    def publish(self) -> None:
        print(self.base_url)

    def logout(self) -> None:
        pass