from story.Story import Story
from story.StoryMock import StoryMock

class StoryFactory:
    @staticmethod
    def create_story(progargs: dict) -> None:
        if progargs.get('mock'):
            print("Creating mock story")
            return StoryMock(progargs)
        else:
            print("Creating story object")
            return Story(progargs)