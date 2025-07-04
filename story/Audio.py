from gtts import gTTS
from gtts.tokenizer.pre_processors import abbreviations, end_of_line
from exceptions import AudioGenerationException
from os import makedirs, path
import pyttsx3
import time

class Audio:
    def __init__(self, file_path: str, file_name: str):
        self.file_path = path.abspath(file_path)
        self.file_name = file_name

        if not self.file_path:
            makedirs(file_path, exist_ok=True)
    
    def _get_audio_gtts(self, text: str, audio_file_path: str):
        gtts_lang = 'hi'  # Hindi language
        reply_obj = gTTS(text=text, lang=gtts_lang, slow=True)
        reply_obj.save(audio_file_path)

    def _get_audio_pyttsx3(self, text: str, audio_file_path: str):
        try:
            engine = pyttsx3.init()

            # Set properties for better audio quality
            engine.setProperty('rate', 150)  # Speed of speech
            engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)

            voices = engine.getProperty('voices')
            for voice in voices:
                if voice.languages and any('hi' in lang.lower() for lang in voice.languages):
                    engine.setProperty('voice', voice.id)
                    break
            
            engine.save_to_file(text, audio_file_path)
            engine.runAndWait()
                            
            # Give a small delay to ensure file is written
            time.sleep(0.5)
        except Exception as e:
            raise AudioGenerationException(
                f"Audio generation failed with pyttsx3: {str(e)}",
                library='pyttsx3',
                language="hi",
                details={"error": str(e), "text_length": len(text)}
            )
        finally:
            try:
                engine.stop()
            except:
                pass
        
    def generate(self, text: str, lib: str = 'gtts'):
        audio_file_path = self.file_path + "/" + lib + "_" + self.file_name
        
        if not path.exists(audio_file_path):
            if lib.lower() == 'gtts':
                self._get_audio_gtts(text, audio_file_path)
            elif lib.lower() == 'pyttsx3':
                self._get_audio_pyttsx3(text, audio_file_path)                        
            else:
                raise AudioGenerationException(
                    f"Unsupported audio generation library: {lib}",
                    library=lib,
                    language="hi",
                    details={"text_length": len(text)}
                )

        # In any case, return the path to the audio file
        return audio_file_path