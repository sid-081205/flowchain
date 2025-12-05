import pyaudio
import webrtcvad
import queue
import logging
from typing import Optional, Generator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Listener")

class Listener:
    def __init__(self, sample_rate: int = 16000, frame_duration_ms: int = 20, vad_aggressiveness: int = 3):
        """
        Initializes the Listener with VAD and PyAudio stream parameters.
        
        Args:
            sample_rate: Audio sample rate in Hz (default 16000 for compatibility).
            frame_duration_ms: Duration of each audio frame in ms (10, 20, or 30ms).
            vad_aggressiveness: VAD aggressiveness mode (0-3).
        """
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.frame_size = int(sample_rate * frame_duration_ms / 1000) * 2 # 2 bytes per sample (16-bit)
        self.vad = webrtcvad.Vad(vad_aggressiveness)
        self.audio = pyaudio.PyAudio()
        self.stream: Optional[pyaudio.Stream] = None
        self.is_listening = False
        self.queue = queue.Queue()

    def start(self):
        """Starts the audio stream."""
        if self.stream:
            return

        def callback(in_data, frame_count, time_info, status):
            self.queue.put(in_data)
            return (None, pyaudio.paContinue)

        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.frame_size // 2, # frames_per_buffer is in samples, not bytes
            stream_callback=callback
        )
        self.stream.start_stream()
        self.is_listening = True
        logger.info("Listener started.")

    def stop(self):
        """Stops the audio stream."""
        if not self.stream:
            return
        
        self.is_listening = False
        self.stream.stop_stream()
        self.stream.close()
        self.stream = None
        logger.info("Listener stopped.")

    def listen(self) -> Generator[bytes, None, None]:
        """
        Yields audio frames from the queue. 
        Note: This effectively yields raw audio chunks. 
        Higher-level logic for silence detection/segmentation should consume this stream.
        """
        while self.is_listening:
            try:
                frame = self.queue.get(timeout=1)
                yield frame
            except queue.Empty:
                continue

    def process_frame(self, frame: bytes) -> bool:
        """
        Returns True if the frame contains speech, False otherwise.
        """
        return self.vad.is_speech(frame, self.sample_rate)

    def __del__(self):
        self.stop()
        self.audio.terminate()
