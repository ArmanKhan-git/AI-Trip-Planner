from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

DUFFEL_API_KEY = os.getenv("DUFFEL_API_KEY")
if not DUFFEL_API_KEY:
    raise ValueError("DUFFEL_API_KEY not found in .env file")

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

if not GOOGLE_PLACES_API_KEY:
    raise ValueError("GOOGLE_PLACES_API_KEY not found in .env file")

EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")

if not EXCHANGE_RATE_API_KEY:
    raise ValueError("EXCHANGE_RATE_API_KEY not found in .env file")