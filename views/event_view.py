from datetime import datetime
from enum import Enum

import discord
from discord import Embed, Member, Message, User
from discord.ext.commands import Context

from db.firebase_service import service


class EmbedFieldLabel(Enum):
    Accepted = "accepted_users"
    Maybe = "maybe_users"
    Declined = "declined_users"


class EventView(discord.ui.View):
    message: Message
    author: User | Member
    event_id: str

    def __init__(self, event_name: str, start_time: str, end_time: str):
        super().__init__()
        self.event_name = event_name
        self.start_time = start_time
        self.end_time = end_time

        self.accepted_users = set()
        self.maybe_users = set()
        self.declined_users = set()

    def _get_default_embed(self) -> Embed:
        embed = discord.Embed(
            title=f"Event: {self.event_name}",
            description=f"You are invited to {self.event_name}\ncreated by: **{self.author.name}**",
            color=0xBEBEFE,
        )

        embed.add_field(
            name="Start Time:",
            value=f"{self.start_time}",
            inline=False,
        )
        embed.add_field(
            name="End Time:",
            value=f"{self.end_time}",
            inline=False,
        )
        return embed

    def _add_all_menu_embed_fields(self, embed: Embed, event_data: dict) -> Embed:
        for embed_label in EmbedFieldLabel:
            embed = embed.add_field(
                name=f"{embed_label.name} ({len(event_data[embed_label.value])})",
                value="\n".join([item for item in event_data[embed_label.value]]),
                inline=True,
            )
        return embed

    # entry point from a command
    async def send(self, ctx: Context):
        self.author = ctx.author

        embed = self._get_default_embed()

        self.accepted_users.add(self.author.name)

        self.event_id = await service.create_db_event(
            author_name=self.author.name,
            name=self.event_name,
            start_time=self.start_time,
            end_time=self.end_time,
            accepted_users=self.accepted_users,
        )
        event_data = await service.get_event_by_id(self.event_id)
        embed = self._add_all_menu_embed_fields(embed, event_data)
        self.message = await ctx.send(embed=embed, view=self)

    async def update_message(self):
        event_data = await service.get_event_by_id(event_id=self.event_id)

        embed = self._get_default_embed()
        embed = self._add_all_menu_embed_fields(embed, event_data)

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
