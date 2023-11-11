import discord
from discord.ext import commands
from discord.ext.commands import Context, Group


class General(commands.Cog, name="general"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="help", description="List all commands the bot has loaded."
    )
    async def help(self, ctx: Context) -> None:
        embed = discord.Embed(
            title="Help",
            description="List of available commands (prefixed with '!' or '/'):",
            color=0xBEBEFE,
        )
        for cog_name in self.bot.cogs:
            if cog_name == "owner" and not (await self.bot.is_owner(ctx.author)):
                continue
            cog = self.bot.get_cog(cog_name.lower())
            data = []
            commands = cog.get_commands()
            for command in commands:
                description = command.description.partition("\n")[0]
                data.append(f"{command.name} - {description}")
                if not isinstance(command, Group):
                    continue
                subcommands = command.walk_commands()
                for subcommand in subcommands:
                    sub_description = subcommand.description.partition("\n")[0]
                    data.append(f"{command.name} {subcommand.name} - {sub_description}")

            help_text = "\n".join(data)

            embed.add_field(
                name=cog_name.replace("_", " ").title(),
                value=f"```{help_text}```",
                inline=False,
            )

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot))
