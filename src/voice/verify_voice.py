import argparse
import time
import logging
from src.voice.listener import Listener
from src.voice.speaker import Speaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VerifyVoice")

def verify_listener():
    print("--- Testing Listener ---")
    listener = Listener(vad_aggressiveness=3)
    listener.start()
    
    print("Listening for 5 seconds... Speak now!")
    start_time = time.time()
    
    try:
        for frame in listener.listen():
            if time.time() - start_time > 5:
                break
            
            is_speech = listener.process_frame(frame)
            status = "Speech" if is_speech else "Silence"
            print(f"\rStatus: {status} | Frame len: {len(frame)}", end="", flush=True)
            
    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()
        print("\nListener test complete.")

def verify_speaker():
    print("--- Testing Speaker ---")
    speaker = Speaker()
    text = "This is a test of the Eleven Labs streaming capability."
    print(f"Speaking: '{text}'")
    speaker.speak(text)
    print("Speaker test complete.")

def verify_loopback():
    print("--- Testing Loopback (Echo) ---")
    print("NOT IMPLEMENTED: Requires VAD segmentation to be useful.")
    # In a real verify, we'd buffer speech and rewrite it to a file or speakers.
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["listener", "speaker", "loopback"], required=True)
    args = parser.parse_args()
    
    if args.mode == "listener":
        verify_listener()
    elif args.mode == "speaker":
        verify_speaker()
    elif args.mode == "loopback":
        verify_loopback()
