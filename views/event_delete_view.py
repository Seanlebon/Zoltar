from datetime import datetime
from enum import Enum

import discord
from discord import Embed, Guild, Interaction, Member, Message, User
from discord.ext.commands import Context

from db.firebase_service import service


class EventDeleteView(discord.ui.View):
    def __init__(self):
        super().__init__()

    async def send(
        self,
        ctx: Context,
        event_name: str,
    ):
        if not await service.delete_event_by_name(event_name=event_name):
            await ctx.send(
                content=f"Sorry event **{event_name}** does not exist.",
                view=self,
                ephemeral=True,
            )
            return

        await ctx.send(
            content=f"The event **{event_name}** was succesfully deleted!", view=self
        )
