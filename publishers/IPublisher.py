from abc import abstractmethod, ABC
from enum import Enum

class PublisherType(Enum):
    TWITTER = 0
    INSTAGRAM = 1
    THREADS = 2
    FACEBOOK = 3
    YOUTUBE = 4

class IPublisher(ABC):
    def __init__(self, credentials: dict=None) -> None:
        super().__init__()

        self.credentials = credentials


    @abstractmethod
    def login(self) -> None:
        pass

    @abstractmethod
    def publish(self, content: dict) -> None:
        pass

    @abstractmethod
    def logout(self) -> None:
        pass