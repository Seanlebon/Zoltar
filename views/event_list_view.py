from datetime import datetime
from enum import Enum

import discord
from discord import Embed, Guild, Interaction, Member, Message, User
from discord.ext.commands import Context

from db.firebase_service import service
from views.event_view import EventView


class EventListView(EventView):
    def __init__(self):
        super().__init__()
        self.guild_events = []

    async def send(self, ctx: Context):
        self.guild = ctx.guild
        self.guild_events = await service.get_events_by_guild_id(guild_id=self.guild.id)
        no_events_message = (
            "\n...Seems like there are no events!" if not self.guild_events else ""
        )
        embed = discord.Embed(
            title="All Events",
            description=f"These are all the upcoming events in {self.guild.name}{no_events_message}",
            color=0xBEBEFE,
        )
        if self.guild_events:
            for guild_event in self.guild_events:
                embed.add_field(
                    name=f"__Event: {guild_event['name']}__",
                    value=f"**Start Time:** {guild_event['start_time']} \n **End Time:** {guild_event['end_time']}",
                    inline=False,
                )

        await ctx.send(embed=embed, view=self)
