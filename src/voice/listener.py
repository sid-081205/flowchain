import sounddevice as sd
import webrtcvad
import queue
import logging
import numpy as np
from typing import Optional, Generator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Listener")

class Listener:
    def __init__(self, sample_rate: int = 16000, frame_duration_ms: int = 20, vad_aggressiveness: int = 3):
        """
        Initializes the Listener with VAD and SoundDevice stream parameters.
        
        Args:
            sample_rate: Audio sample rate in Hz.
            frame_duration_ms: Duration of each audio frame in ms (10, 20, or 30ms).
            vad_aggressiveness: VAD aggressiveness mode (0-3).
        """
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.frame_size = int(sample_rate * frame_duration_ms / 1000) # samples per frame
        self.vad = webrtcvad.Vad(vad_aggressiveness)
        self.stream: Optional[sd.InputStream] = None
        self.is_listening = False
        self.queue = queue.Queue()

    def start(self):
        """Starts the audio stream."""
        if self.stream:
            return

        def callback(indata, frames, time, status):
            if status:
                logger.warning(f"Audio status: {status}")
            # indata is numpy array (frames, channels)
            # We need raw bytes for VAD
            self.queue.put(indata.tobytes())

        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                blocksize=self.frame_size,
                device=None, # Use default input device
                channels=1,
                dtype='int16',
                callback=callback
            )
            self.stream.start()
            self.is_listening = True
            logger.info("Listener started.")
        except Exception as e:
            logger.error(f"Failed to start audio stream: {e}")
            self.is_listening = False

    def stop(self):
        """Stops the audio stream."""
        if not self.stream:
            return
        
        self.is_listening = False
        self.stream.stop()
        self.stream.close()
        self.stream = None
        logger.info("Listener stopped.")

    def listen(self) -> Generator[bytes, None, None]:
        """
        Yields audio frames from the queue. 
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
        if len(frame) != self.frame_size * 2: # 2 bytes per sample
            # This might happen if sounddevice returns partial block?
            # But we set blocksize, so it should be exact mostly.
            # However, VAD requires exact frame size.
            return False
            
        return self.vad.is_speech(frame, self.sample_rate)

    def __del__(self):
        self.stop()
