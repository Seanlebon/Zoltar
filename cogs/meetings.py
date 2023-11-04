import discord
from discord.ext import commands

class Meetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot) -> None:
    await bot.add_cog(Meetings(bot))