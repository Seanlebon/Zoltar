from datetime import datetime

from discord.ext import commands
from discord.ext.commands import Context

from core.bot import ZoltarBot
from db import service
from utils.logger import logger
from views import EventDeleteView, EventInfoView, EventListView, EventQuickView


class EventScheduler(commands.Cog, name="event_scheduler"):
    def __init__(self, bot: ZoltarBot):
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
        description="Zoltar will create an event reminder in US/Eastern time given an event name and start and end times",
    )
    async def quick(
        self,
        ctx: Context,
        event_name: str,
        start_time: str,
        end_time: str,
    ) -> None:
        if await service.get_event_by_name(event_name):
            await ctx.send(
                content=f"Sorry **{event_name}** is already an event name. Please choose another name.",
                ephemeral=True,
            )
            return
        # Checking date_time strings:
        # start_time_dt = set_dt(start_time)
        # end_time_dt = set_dt(end_time)
        view = EventQuickView(event_name, start_time, end_time)
        await view.send(ctx)

    @event.command(
        name="all",
        description="Zoltar will create list all the on going events in this server",
    )
    async def all(self, ctx: Context):
        view = EventListView()
        await view.send(ctx)

    @event.command(
        name="info",
        description="Zoltar will get the info for an event",
    )
    async def info(
        self,
        ctx: Context,
        event_name: str,
    ):
        view = EventInfoView()
        await view.send(ctx, event_name)

    @event.command(
        name="delete",
        description="Zoltar will delete and remove an event from this server",
    )
    async def delete(
        self,
        ctx: Context,
        event_name: str,
    ):
        view = EventDeleteView()
        await view.send(ctx, event_name)


async def setup(bot: ZoltarBot) -> None:
    await bot.add_cog(EventScheduler(bot))


def set_dt(dt_string: str) -> datetime:
    try:
        return datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        logger.exception("The provided argument is not a valid datetime.")
