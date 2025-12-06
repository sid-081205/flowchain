import os
import sys
from dotenv import load_dotenv
from google import genai

# Load env to get the key
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in environment.")
    sys.exit(1)

print(f"🔑 Using Key: {api_key[:5]}...{api_key[-3:]}")

try:
    client = genai.Client(api_key=api_key)
    print("\n📡 Querying Google AI for available models...")
    
    # List models
    # The SDK structure in the error log suggests google.genai.Client
    # usage might differ slightly, but let's try the standard way first.
    # If this fails, we'll know the SDK version is quirky.
    
    # Based on error logs, the SDK is interacting with `client.models`
    # The error message said: "Call ListModels"
    
    pager = client.models.list()
    
    print("\n✅ Available Models:")
    found_any = False
    for model in pager:
        print(f" - {model.name}")
        # print(f"   (Debug: {model})")
             
    if not found_any:
        print("⚠️  No models found that support 'generateContent'.")
        
except Exception as e:
    print(f"\n❌ API Call Failed: {e}")
    print("Possible causes:")
    print("1. API Key is invalid.")
    print("2. Google AI Studio is not enabled for this project.")
    print("3. Region restrictions.")
