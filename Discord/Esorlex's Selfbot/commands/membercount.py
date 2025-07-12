from discord.ext import commands

class MemberCount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='membercount')
    async def member_count(self, ctx):
        await ctx.message.delete()
        guild = ctx.guild
        if guild:
            total_members = guild.member_count
            await ctx.send(f"👥 This server has **{total_members}** members!")
        else:
            await ctx.send("❌ Could not get server information.")

async def setup(bot):
    await bot.add_cog(MemberCount(bot))
