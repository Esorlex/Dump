import discord
from discord.ext import commands

class Credits(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="credits")
    async def credits(self, ctx):
        await ctx.message.delete()
        credits_text = "# 👑 Credits\n# $Esorlex$\n# Virexb\n# Sus\n# Wast3d\n# BLADE"
        await ctx.send(credits_text)

async def setup(bot):
    await bot.add_cog(Credits(bot))
