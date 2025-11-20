import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config(object):
    LOGGER = True

    OWNER_ID = os.getenv("OWNER_ID")
    sudo_users = os.getenv("SUDO_USERS").split(",")  # Convert CSV to list
    GROUP_ID = int(os.getenv("GROUP_ID"))
    TOKEN = os.getenv("TOKEN")
    mongo_url = os.getenv("MONGO_URL")
    PHOTO_URL = os.getenv("PHOTO_URL").split(",")  # Convert CSV to list
    SUPPORT_CHAT = os.getenv("SUPPORT_CHAT")
    UPDATE_CHAT = os.getenv("UPDATE_CHAT")
    BOT_USERNAME = os.getenv("BOT_USERNAME")
    CHARA_CHANNEL_ID = int(os.getenv("CHARA_CHANNEL_ID"))
    api_id = int(os.getenv("API_ID"))
    api_hash = os.getenv("API_HASH")


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
