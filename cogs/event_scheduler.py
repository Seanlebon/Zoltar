import discord
from discord.ext import commands
from discord.ext.commands import Context

from utils.logger import logger


class EventScheduler(commands.Cog, name="event_scheduler"):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logger

    @commands.hybrid_group(
        name="event",
        description="Base event command. Does not do anything",
    )
    async def event(self, ctx: Context) -> None:
        if ctx.invoked_subcommand:
            passed = ctx.subcommand_passed
            msgs = (
                "No command was passed, please look at !help to continue",
                f"No, {passed} does not belong to the event command please look at !help to continue",
            )
            self.logger.info(msgs[0] if passed else msgs[1])
            await ctx.send(msgs[0] if passed else msgs[1])

    @event.command(
        name="create",
        description="A event creation modal will pop up, and can create an event with configurations.",
    )
    async def create(self, ctx: Context) -> None:
        self.logger.info("create my guys")
        pass


async def setup(bot) -> None:
    await bot.add_cog(EventScheduler(bot))
