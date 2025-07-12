from discord.ext import commands
import discord

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def serverinfo(self, ctx, server_id: int = None):
        await ctx.message.delete()

        if server_id is None:
            server = ctx.guild
        else:
            server = self.bot.get_guild(server_id)

        if not server:
            await ctx.send("Server not found or the bot is not in that server.")
            return

        server_name = server.name
        server_id = server.id
        member_count = server.member_count
        owner = server.owner
        creation_date = server.created_at.strftime('%b %d, %Y')
        icon_url = server.icon.url if server.icon else "No Icon"
        description = server.description if server.description else "No Description"
        verification_level = server.verification_level

        server_info_message = (
            f"**Server Info - {server_name}**\n"
            f"**Server ID:** {server_id}\n"
            f"**Owner:** {owner}\n"
            f"**Member Count:** {member_count}\n"
            f"**Creation Date:** {creation_date}\n"
            f"**Description:** {description}\n"
            f"**Verification Level:** {verification_level}\n"
            f"**Icon:** {icon_url}"
        )

async def setup(bot):
    await bot.add_cog(ServerInfo(bot))