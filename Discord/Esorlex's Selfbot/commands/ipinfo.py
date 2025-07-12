import discord
from discord.ext import commands
import aiohttp

class IPInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ipinfo(self, ctx, ip: str = None):
        await ctx.message.delete()

        if ip is None:
            await ctx.send("❌ Please provide an IP address to lookup.")
            return

        url = f"https://ipinfo.io/{ip}/json"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send("⚠️ Failed to fetch info for that IP.")
                    return
                data = await resp.json()

        msg = (
            f"🌐 **IP Info for:** {ip}\n"
            f"🆔 **IP:** {data.get('ip', 'N/A')}\n"
            f"🏷️ **Hostname:** {data.get('hostname', 'N/A')}\n"
            f"🏙️ **City:** {data.get('city', 'N/A')}\n"
            f"🌍 **Region:** {data.get('region', 'N/A')}\n"
            f"🇺🇳 **Country:** {data.get('country', 'N/A')}\n"
            f"📍 **Location (lat,long):** {data.get('loc', 'N/A')}\n"
            f"🏢 **Organization:** {data.get('org', 'N/A')}\n"
            f"⏰ **Timezone:** {data.get('timezone', 'N/A')}"
        )

        await ctx.send(msg)

async def setup(bot):
    await bot.add_cog(IPInfo(bot))
