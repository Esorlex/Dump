import discord
from discord.ext import commands
import asyncio
import aiohttp

class BanAll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def banall(self, ctx, *, reason="No reason provided"):
        await ctx.message.delete()
        guild = ctx.guild
        if not guild:
            await ctx.send("❌ This command can only be used in a server.")
            return
        members_to_ban = [member for member in guild.members]

        headers = {
            "Authorization": f"{self.bot.http.token}",
            "X-Audit-Log-Reason": reason,
            "User-Agent": "Mozilla/5.0"
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            for member in members_to_ban:
                try:
                    url = f"https://discord.com/api/v10/guilds/{guild.id}/bans/{member.id}"
                    async with session.put(url) as response:
                        if response.status == 204:
                            print(f"Banned {member}")
                        else:
                            text = await response.text()
                            print(f"Failed to ban {member}: {response.status} - {text}")
                    await asyncio.sleep(0.5)  # rate limit handling
                except Exception as e:
                    print(f"Error banning {member}: {e}")

async def setup(bot):
    await bot.add_cog(BanAll(bot))
