from Story import Story
from StoryMock import StoryMock

class StoryFactory:
    @staticmethod
    def create_story(progargs: dict) -> None:
        if progargs.get('mock'):
            return StoryMock(progargs)
        else:
            return Story(progargs)