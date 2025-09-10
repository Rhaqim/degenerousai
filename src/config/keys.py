import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Example: Load API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANOTHER_API_KEY = os.getenv("ANOTHER_API_KEY")

# Add more keys as needed
