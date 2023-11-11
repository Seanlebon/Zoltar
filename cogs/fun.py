import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import Context


class Fun(commands.Cog, name="fun"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="randomfact", description="Get a random fact.")
    async def randomfact(self, ctx: Context) -> None:
        """
        Get a random fact.

        :param context: The hybrid command context.
        """
        # This will prevent your bot from stopping everything when doing a web request - see: https://discordpy.readthedocs.io/en/stable/faq.html#how-do-i-make-a-web-request
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://uselessfacts.jsph.pl/random.json?language=en"
            ) as request:
                if request.status == 200:
                    data = await request.json()
                    embed = discord.Embed(description=data["text"], color=0xD75BF4)
                else:
                    embed = discord.Embed(
                        title="Error!",
                        description="There is something wrong with the API, please try again later",
                        color=0xE02B2B,
                    )
                await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))
