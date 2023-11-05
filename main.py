import discord
import os
from dotenv import load_dotenv
from core.bot import ZoltarBot

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

def main():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = ZoltarBot(intents=intents)
    bot.run(TOKEN)

if __name__ == "__main__":
    main()