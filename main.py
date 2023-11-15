import asyncio
import os

import discord
from dotenv import load_dotenv

from config import TOKEN
from core.bot import ZoltarBot
from db.firebase_service import FirebaseService

load_dotenv()


def main():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = ZoltarBot(intents=intents)
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
