import os
from dotenv import load_dotenv

# Load the .env file once
load_dotenv()

# Grab the key and store it in a standard Python variable
MAPTILER_API_KEY = os.getenv("MAPTILER_API_KEY")