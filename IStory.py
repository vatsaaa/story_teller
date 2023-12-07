from abc import ABC, abstractmethod

class IStory(ABC):
    def __init__(self) -> None:
        super().__init__()
    
    @abstractmethod
    def get_text(self):
        pass

    @abstractmethod
    def translate(self):
        pass

    @abstractmethod
    def get_images(self):
        pass

    @abstractmethod
    def get_video(self):
        pass

    @abstractmethod
    def get_audio(self):
        pass

    @abstractmethod
    def get_sceneries(self):
        pass