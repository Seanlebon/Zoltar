from discord import Member, User
from discord.ext.commands import Context

from db import fb_service
from views.event_view import EventView


class EventInfoView(EventView):
    author: User | Member

    def __init__(self):
        super().__init__()

    async def send(self, ctx: Context, event_name: str):
        self.author = ctx.author
        event_data = await fb_service.get_event_by_name(event_name)
        if not event_data:
            await ctx.send(
                content=f"Sorry event **{event_name}** does not exist.",
                view=self,
                ephemeral=True,
            )
            return

        embed = self._get_default_embed(
            event_data["name"],
            event_data["start_time"],
            event_data["end_time"],
            event_data["author_name"],
            True,
        )
        embed = self._add_all_menu_embed_fields(embed, event_data)
        await ctx.send(embed=embed, view=self)
