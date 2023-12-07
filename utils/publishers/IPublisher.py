from abc import abstractmethod, ABC
from enum import Enum

class Publishers(Enum):
    FACEBOOK = 1
    INSTAGRAM = 2
    TWITTER = 3
    YOUTUBE = 4

class IPublisher(ABC):
    def __init__(self) -> None:
        super().__init__()
    
    @abstractmethod
    def publish(self, content: dict) -> None:
        pass
