import os 
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    print("API Sucessfully")
else:
    print("not sucessfully")