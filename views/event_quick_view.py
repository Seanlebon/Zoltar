from datetime import datetime
from enum import Enum

import discord
from discord import Embed, Guild, Interaction, Member, Message, User
from discord.ext.commands import Context

from db.firebase_service import service
from views.event_view import EventView


class EventQuickView(EventView):
    event_id: str

    def __init__(self, event_name: str, start_time: str, end_time: str):
        super().__init__()
        self.event_name = event_name
        self.start_time = start_time
        self.end_time = end_time

        self.accepted_users = set()
        self.maybe_users = set()
        self.declined_users = set()

    # entry point from a command
    async def send(self, ctx: Context):
        self.author = ctx.author
        self.guild = ctx.guild
        embed = self._get_default_embed(
            self.event_name, self.start_time, self.end_time, self.author.name
        )

        self.accepted_users.add(self.author.name)

        self.event_id = await service.create_db_event(
            guild_id=self.guild.id,
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

        embed = self._get_default_embed(
            event_data["name"],
            event_data["start_time"],
            event_data["end_time"],
            event_data["author_name"],
        )
        embed = self._add_all_menu_embed_fields(embed, event_data)

        await self.message.edit(embed=embed, view=self)

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: Interaction, button: discord.ui.Button):
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
    async def maybe(self, interaction: Interaction, button: discord.ui.Button):
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
    async def decline(self, interaction: Interaction, button: discord.ui.Button):
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
