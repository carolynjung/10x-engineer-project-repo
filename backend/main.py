"""PromptLab API Server

Run with: python main.py
"""

import uvicorn
from app.api import app

if __name__ == "__main__":
    #uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
