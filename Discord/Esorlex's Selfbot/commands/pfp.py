import discord
from discord.ext import commands

class PFP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pfp(self, ctx, member: discord.User = None):
        await ctx.message.delete()
        if member is None:
            member = ctx.author  

        avatar = member.avatar
        if avatar is None:
            await ctx.send(f"{member.name} does not have a profile picture.")
            return

        avatar_url = avatar.url
        await ctx.send(f"{member.name}'s Profile Picture:\n{avatar_url}")

async def setup(bot):
    await bot.add_cog(PFP(bot))
