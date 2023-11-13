from datetime import datetime
from typing import Optional

import discord
from discord import Member, Message, User
from discord.ext import commands
from discord.ext.commands import Context

from utils.logger import logger


class EventView(discord.ui.View):
    message: Message
    author: User | Member

    def __init__(self, event_name: str, event_date: str):
        super().__init__()
        self.event_name = event_name
        self.event_date = event_date

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
        self.message = await ctx.send(embed=embed, view=self)

    async def update_message(self):
        await self.message.edit(embed=self.create_embed(), view=self)

    def create_embed(self):
        # make this more readable
        embed = discord.Embed(
            title=f"Event: {self.event_name}",
            description=f"You are invited to {self.event_name}\ncreated by: {self.author.name}",
            color=0xBEBEFE,
        )
        event_field_items = [
            ("Accepted", self.accepted_users, self.accept_count),
            ("Maybe", self.maybe_users, self.maybe_count),
            ("Declined", self.declined_users, self.decline_count),
        ]

        for field_name, field_values, field_count in event_field_items:
            embed.add_field(
                name=f"{field_name} ({field_count})",
                value="\n".join([item for item in field_values]),
                inline=True,
            )
        return embed

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if interaction.user.name not in self.accepted_users:
            self.accept_count = max(0, self.accept_count + 1)
            self.maybe_count = max(0, self.maybe_count - 1)
            self.decline_count = max(0, self.decline_count - 1)

            self.accepted_users.add(interaction.user.name)
            self.maybe_users.discard(interaction.user.name)
            self.declined_users.discard(interaction.user.name)
            await self.update_message()

    @discord.ui.button(label="Maybe", style=discord.ButtonStyle.grey)
    async def maybe(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if interaction.user.name not in self.maybe_users:
            self.accept_count = max(0, self.accept_count - 1)
            self.maybe_count = max(0, self.maybe_count + 1)
            self.decline_count = max(0, self.decline_count - 1)

            self.accepted_users.discard(interaction.user.name)
            self.maybe_users.add(interaction.user.name)
            self.declined_users.discard(interaction.user.name)
            await self.update_message()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        if interaction.user.name not in self.declined_users:
            self.accept_count = max(0, self.accept_count - 1)
            self.maybe_count = max(0, self.maybe_count - 1)
            self.decline_count = max(0, self.decline_count + 1)

            self.accepted_users.discard(interaction.user.name)
            self.maybe_users.discard(interaction.user.name)
            self.declined_users.add(interaction.user.name)
            await self.update_message()


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
        description="Zoltar will create an event reminder (no end time) given an event name and event datetime",
    )
    async def quick(self, ctx: Context, event_name: str, start: str) -> None:
        # embed = discord.Embed(title="Test", description="amongus")

        # embed.add_field(
        #     name="accepted", value=f"{ctx.author}\n{ctx.author}", inline=True
        # )
        # embed.add_field(name="maybe", value=ctx.author, inline=True)
        # embed.add_field(name="declined", value=ctx.author, inline=True)

        # await ctx.send(embed=embed)
        # pass
        view = EventView(event_name, start)
        await view.send(ctx)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(EventScheduler(bot))
