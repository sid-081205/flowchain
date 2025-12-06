import speech_recognition as sr
from elevenlabs import ElevenLabs
from elevenlabs.play import play
from src import config

class VoiceAssistant:
    def __init__(self):
        if not config.ELEVENLABS_API_KEY:
            raise ValueError("ELEVENLABS_API_KEY is not set")
            
        self.client = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)
        self.recognizer = sr.Recognizer()
        
        # Give user time to think (pause threshold)
        self.recognizer.pause_threshold = 3.0
        # Increase energy threshold dynamic adjustment speed
        self.recognizer.dynamic_energy_adjustment_ratio = 1.5

    def listen(self) -> str:
        """
        Listens to the microphone and returns text.
        Returns empty string on failure.
        """
        try:
            with sr.Microphone() as source:
                print("🎤 Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # timeout: max seconds to wait for speech to start
                # phrase_time_limit: max seconds to allow for a single utterance
                audio = self.recognizer.listen(source, timeout=5.0, phrase_time_limit=15.0)

            print("📝 Converting speech to text...")
            # Using google speech recognition as it's free and decent default
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text

        except sr.RequestError as e:
            print(f"❌ Could not request results; {e}")
            return ""
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return ""
        except Exception as e:
            print(f"❌ Error listening: {e}")
            return ""

    def speak(self, text: str):
        """
        Generates audio for the text and plays it.
        """
        if not text:
            return

        try:
            # Generate audio using ElevenLabs Client
            # Voice ID for Rachel: 21m00Tcm4TlvDq8ikWAM
            audio = self.client.text_to_speech.convert(
                voice_id="21m00Tcm4TlvDq8ikWAM",
                model_id="eleven_multilingual_v2",
                text=text
            )
            # Play the audio
            play(audio)
        except Exception as e:
            print(f"❌ Error generating/playing audio: {e}")
