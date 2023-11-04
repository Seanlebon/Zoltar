import json
import os
import platform
import random
import sys

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
from dotenv import load_dotenv
from utils.logger import logger

intents = discord.Intents.default()

class ZoltarBot(commands.Bot):
    def __init__(self, intents) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or('!'),
            intents=intents,
            help_command=None,
        )
        self.logger = logger

    @tasks.loop(minutes=1.0)
    async def status_task(self) -> None:
        """
        Setup the game status task of the bot.
        """
        statuses = ["with you!", "with Krypton!", "with humans!"]
        await self.change_presence(activity=discord.Game(random.choice(statuses)))

    async def load_cogs(self) -> None:
        """
        The code in this function is executed whenever the bot will start.
        """
        for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/../cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await self.load_extension(f"cogs.{extension}")
                    self.logger.info(f"Loaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.error(
                        f"Failed to load extension {extension}\n{exception}"
                    )

    async def setup_hook(self) -> None:
        """
        This will just be executed when the bot starts the first time.
        """
        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"discord.py API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(
            f"Running on: {platform.system()} {platform.release()} ({os.name})"
        )
        self.logger.info("-------------------")
        await self.load_cogs()
        # self.status_task.start()