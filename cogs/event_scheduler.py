import discord
from discord.ext import commands
from discord.ext.commands import Context

from utils.logger import logger


class EventScheduler(commands.Cog, name="event_scheduler"):
    def __init__(self, bot: commands.Bot):
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
                "The !event command requires a subcommand, please look at !help to continue",
                f"**{passed}** does not belong to the event command, please look at !help to continue",
            )
            self.logger.info(msgs[1] if passed else msgs[0])
            await ctx.defer(ephemeral=True)
            await ctx.reply(
                msgs[1] if passed else msgs[0],
                ephemeral=True,
            )

    @event.command(
        name="create",
        description="Zoltar will create an event for you in a private discord",
    )
    async def create(self, ctx: Context) -> None:
        self.logger.info("Making event")
        pass

    @event.command(
        name="quick",
        description="Zoltar will create an event given an event name and event date",
    )
    async def quick(self, ctx: Context) -> None:
        self.logger.info("Making quick event")
        ctx.reply("Can you see this?")
        pass


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(EventScheduler(bot))
