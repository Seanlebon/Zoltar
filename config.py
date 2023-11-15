from os import environ, path

from dotenv import load_dotenv

# Specificy a `.env` file containing key/value config values
basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

# General Config
TOKEN = environ.get("DISCORD_TOKEN")
GUILD = environ.get("DISCORD_GUILD")
GOOGLE_CREDS = environ.get("GOOGLE_APPLICATION_CREDENTIALS")
FIRESTORE_PROJECT_ID = environ.get("FIRESTORE_PROJECT_ID")
