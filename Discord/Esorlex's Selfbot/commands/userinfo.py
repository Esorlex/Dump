from discord.ext import commands
import discord

class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def userinfo(self, ctx, member: discord.User = None):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        member = member or ctx.author
        avatar = member.display_avatar.url

        joined_at = "Unknown"
        roles = "None"
        status = "Unknown"

        if ctx.guild:
            guild_member = ctx.guild.get_member(member.id)
            if guild_member:
                joined_at = guild_member.joined_at.strftime('%b %d, %Y') if guild_member.joined_at else "Unknown"
                roles = ', '.join(role.name for role in guild_member.roles[1:]) or "None"
                status = str(guild_member.status).title()

        user_info_message = (
            f"**Esorlex's selfbot - {member.display_name}**\n"
            f"**ID:** {member.id}\n"
            f"**Joined Server:** {joined_at}\n"
            f"**Account Created:** {member.created_at.strftime('%b %d, %Y')}\n"
            f"**Status:** {status}\n"
            f"**Roles:** {roles}\n"
            f"**Avatar:** {avatar}"
        )

        await ctx.send(user_info_message)

async def setup(bot):
    await bot.add_cog(UserInfo(bot))