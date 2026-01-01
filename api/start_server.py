#!/usr/bin/env python3
"""
Start the Still API server.
"""

import uvicorn
import os

if __name__ == "__main__":
    print("🕯️  Starting Still API server...")
    print("The ritual backend is awakening...")
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )