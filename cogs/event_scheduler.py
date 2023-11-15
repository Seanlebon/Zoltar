from datetime import datetime
from typing import Optional

import discord
from discord import Member, Message, User
from discord.ext import commands
from discord.ext.commands import Context

from core.bot import ZoltarBot
from db.firebase_service import service
from utils.logger import logger


class EventView(discord.ui.View):
    message: Message
    author: User | Member
    event_id: str

    def __init__(self, event_name: str, start_date: str, end_date: str):
        super().__init__()
        self.event_name = event_name
        self.start_date = start_date
        self.end_date = end_date

        self.accepted_users = set()
        self.maybe_users = set()
        self.declined_users = set()

        self.accept_count = 0
        self.maybe_count = 0
        self.decline_count = 0

    # entry point from a command
    async def send(self, ctx: Context):
        self.author = ctx.author

        embed = discord.Embed(
            title=f"Event: {self.event_name}",
            description=f"You are invited to {self.event_name}\ncreated by: {self.author.name}",
            color=0xBEBEFE,
        )
        self.event_id = await service.create_db_event(
            author_name=self.author.name,
            name=self.event_name,
            start_date=self.start_date,
            end_date=self.end_date,
        )
        self.message = await ctx.send(embed=embed, view=self)

    async def update_message(self):
        event_data = await service.get_event_by_id(event_id=self.event_id)

        embed = discord.Embed(
            title=f"Event: {event_data['name']}",
            description=f"You are invited to {event_data['name']}\ncreated by: {event_data['author_name']}",
            color=0xBEBEFE,
        )
        event_field_items = [
            (
                "Accepted",
                event_data["accepted_users"],
                len(event_data["accepted_users"]),
            ),
            ("Maybe", event_data["maybe_users"], len(event_data["maybe_users"])),
            (
                "Declined",
                event_data["declined_users"],
                len(event_data["declined_users"]),
            ),
        ]

        for field_name, field_values, field_count in event_field_items:
            embed.add_field(
                name=f"{field_name} ({field_count})",
                value="\n".join([item for item in field_values]),
                inline=True,
            )

        await self.message.edit(embed=embed, view=self)

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if interaction.user.name not in self.accepted_users:
            self.accepted_users.add(interaction.user.name)
            self.maybe_users.discard(interaction.user.name)
            self.declined_users.discard(interaction.user.name)
            await service.update_event_by_id(
                event_id=self.event_id,
                accepted_users=self.accepted_users,
                maybe_users=self.maybe_users,
                declined_users=self.declined_users,
            )
            await self.update_message()

    @discord.ui.button(label="Maybe", style=discord.ButtonStyle.grey)
    async def maybe(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if interaction.user.name not in self.maybe_users:
            self.accepted_users.discard(interaction.user.name)
            self.maybe_users.add(interaction.user.name)
            self.declined_users.discard(interaction.user.name)
            print(self.accepted_users)
            await service.update_event_by_id(
                event_id=self.event_id,
                accepted_users=self.accepted_users,
                maybe_users=self.maybe_users,
                declined_users=self.declined_users,
            )
            await self.update_message()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        if interaction.user.name not in self.declined_users:
            self.accepted_users.discard(interaction.user.name),
            self.maybe_users.discard(interaction.user.name),
            self.declined_users.add(interaction.user.name),
            await service.update_event_by_id(
                event_id=self.event_id,
                accepted_users=self.accepted_users,
                maybe_users=self.maybe_users,
                declined_users=self.declined_users,
            )
            await self.update_message()


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
        description="Zoltar will create an event reminder (no end time) given an event name and event datetime",
    )
    async def quick(
        self, ctx: Context, event_name: str, start_date: str, end_date: str
    ) -> None:
        view = EventView(event_name, start_date, end_date)
        await view.send(ctx)


async def setup(bot: ZoltarBot) -> None:
    await bot.add_cog(EventScheduler(bot))
