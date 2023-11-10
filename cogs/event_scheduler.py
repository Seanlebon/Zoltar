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
        if not ctx.invoked_subcommand:
            passed = ctx.subcommand_passed
            msgs = (
                "The !event command requires a subcommand, please use !help to continue",
                f"**{passed}** does not belong to the event command please look at !help to continue",
            )
            self.logger.info(f"WHAT DA HELL {passed}")
            self.logger.info(msgs[1] if passed else msgs[0])
            await ctx.send(msgs[1] if passed else msgs[0])
        self.logger.info(f"{ctx.invoked_subcommand} we out heree")

    @event.command(
        name="create",
        description="A event creation modal will pop up, and can create an event with configurations.",
    )
    async def create(self, ctx: Context) -> None:
        self.logger.info("create my guys")
        pass


async def setup(bot) -> None:
    await bot.add_cog(EventScheduler(bot))
