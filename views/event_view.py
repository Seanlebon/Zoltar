from abc import ABC, abstractmethod
from enum import Enum

import discord
from discord import Embed, Guild, Member, Message, User
from discord.ext.commands import Context


class EmbedFieldLabel(Enum):
    Accepted = "accepted_users"
    Maybe = "maybe_users"
    Declined = "declined_users"


class EventView(discord.ui.View, ABC):
    message: Message
    author: User | Member
    guild: Guild

    def __init__(self):
        super().__init__()

    def _get_default_embed(
        self,
        event_name: str,
        start_time: str,
        end_time: str,
        author_name: str,
        event_created: bool = False,
    ) -> Embed:
        embed_description = (
            f"You are invited to {event_name}" if not event_created else ""
        )
        embed = discord.Embed(
            title=f"Event: {event_name}",
            description=f"{embed_description}\ncreated by: **{author_name}**",
            color=0xBEBEFE,
        )

        embed.add_field(
            name="Start Time:",
            value=f"{start_time}",
            inline=False,
        )
        embed.add_field(
            name="End Time:",
            value=f"{end_time}",
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

    @abstractmethod
    async def send(self, ctx: Context):
        """
        This is an entry point for commands to send ui in chat
        Ex.
            self.author = ctx.author
            self.guild = ctx.guild
        """
        raise NotImplementedError
