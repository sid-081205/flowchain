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
            # Join the text stream for now as 'text' argument expects str, 
            # OR check if it supports iterator. The help says text: str.
            # If we want to stream TEXT input, we usually need a specific functionality/method or input stream.
            # RealtimeTextToSpeechClient usually has a websocket method for text streaming.
            # But here `convert` expects `text: str`.
            # If we pass an iterator to `convert`, it might fail if type check is strict.
            # However, for LOW LATENCY, we often want to stream text chunks.
            # Let's inspect if there is `convert_realtime` which might be a socket.
            # The dir output showed `convert_realtime`.
            # For this MVP, I will accumulate text or assume the input is a full string if the user calls speaks.
            # But the signature `speak_stream` implies text stream.
            
            # If the SDK doesn't support text iterator in `convert`, we should use `convert_realtime` (WebSocket).
            # But `convert_realtime` usage is more complex.
            # Let's check `convert_realtime` help?
            # Or just simplify: assume we send short sentences.
            
            # For now, I will assume the input is a single text chunk for `convert`.
            # If `text_stream` is an iterator, I'll join it.
            # This defeats the purpose of streaming text, but gets us working.
            # To do true text streaming, we need `input_stream` over websocket.
            
            full_text = "".join(text_stream) 
            
            audio_stream = self.client.text_to_speech.convert(
                text=full_text,
                voice_id=voice_id,
                model_id="eleven_turbo_v2_5", # Turbo for low latency
                optimize_streaming_latency=3
            )
            stream(audio_stream)
        except Exception as e:
            logger.error(f"Error in speak_stream: {e}")

    def speak(self, text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM"):
        """
        Speaks a single string of text.
        """
        try:
            audio_stream = self.client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_turbo_v2_5",
                optimize_streaming_latency=3
            )
            stream(audio_stream)
        except Exception as e:
            logger.error(f"Error in speak: {e}")
