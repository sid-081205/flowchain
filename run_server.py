#!/usr/bin/env python3
"""
Simple script to run the FlowChain server.
Usage: python run_server.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    import uvicorn
    import warnings
    import logging
    
    # Suppress deprecation warnings and LLM manager cleanup warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    logging.getLogger("spoon_ai.llm.manager").setLevel(logging.ERROR)
    
    from src.server import app
    
    print("=" * 60)
    print("🚀 Starting FlowChain Server")
    print("=" * 60)
    print("📡 Server will be available at: http://localhost:8000")
    print("🔌 WebSocket endpoint: ws://localhost:8000/ws")
    print("=" * 60)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

