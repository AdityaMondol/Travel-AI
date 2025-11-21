import uvicorn
import os
import sys

# Add current directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Starting AI Agent Army Server...")
    print("📍 Open http://localhost:8000 in your browser")
    
    # Use string import for reload to work properly
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
