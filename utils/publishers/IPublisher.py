from abc import abstractmethod, ABC

class IPublisher(ABC):
    def __init__(self) -> None:
        super().__init__()
    
    @abstractmethod
    def publish(self, content: dict) -> None:
        pass
