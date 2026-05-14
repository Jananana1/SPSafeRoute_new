import sys
import os
import uvicorn

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Debug: check if Firebase credentials file is in the expected location
cwd = os.getcwd()
cred_file = os.path.join(cwd, "firebase-adminsdk.json")
print(f"Current working directory: {cwd}")
print(f"Looking for credentials at: {cred_file}")
print(f"File exists: {os.path.exists(cred_file)}")

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)