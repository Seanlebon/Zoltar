import discord
from discord.ext import commands
from discord.ext.commands import Context


class SchedulerUserSelect(discord.ui.UserSelect):
    def __init__(self) -> None:
        super().__init__(
            placeholder="Choose Members",
            min_values=1,
            max_values=25,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        user_selection = self.values

        result_embed = discord.Embed(color=0xBEBEFE)
        result_embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar.url
        )

        result_embed.description = f"**You won!**\n"
        result_embed.colour = 0x57F287

        await interaction.response.edit_message(
            embed=result_embed, content=None, view=None
        )


class SchedulerRoleSelect(discord.ui.RoleSelect):
    def __init__(self) -> None:
        super().__init__(
            placeholder="Choose By Role",
            min_values=1,
            max_values=25,
        )


class SchedulerView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__()
        self.add_item(SchedulerUserSelect())
        self.add_item(SchedulerRoleSelect())


class Scheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="event",
        description="Create an event reminder for members selected or for members by role.",
    )
    async def rock_paper_scissors(self, context: Context) -> None:
        """
        Play the rock paper scissors game against the bot.

        :param context: The hybrid command context.
        """
        view = SchedulerView()
        await context.send("Please make your choice", view=view)


async def setup(bot) -> None:
    await bot.add_cog(Scheduler(bot))
