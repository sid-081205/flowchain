from elevenlabs.client import ElevenLabs
from elevenlabs import stream
import logging
from typing import Iterator, Union
from src.config import ELEVENLABS_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Speaker")

class Speaker:
    def __init__(self):
        """
        Initializes the Speaker with ElevenLabs client.
        """
        if not ELEVENLABS_API_KEY:
            logger.warning("ELEVENLABS_API_KEY not set in config. Voice output will fail.")
        
        self.client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

    def speak_stream(self, text_stream: Iterator[str], voice_id: str = "21m00Tcm4TlvDq8ikWAM"):
        """
        Streams audio from ElevenLabs based on an input text generator.
        
        Args:
            text_stream: Iterator yielding strings (tokens/words).
            voice_id: ElevenLabs voice ID to use.
        """
        try:
            audio_stream = self.client.generate(
                text=text_stream,
                voice=voice_id,
                stream=True
            )
            stream(audio_stream)
        except Exception as e:
            logger.error(f"Error in speak_stream: {e}")

    def speak(self, text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM"):
        """
        Speaks a single string of text.
        """
        self.speak_stream(iter([text]), voice_id)
