import discord
from discord.ext import commands
import aiohttp
import asyncio

class WebhookSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def webhookspam(self, ctx, amount: int = None, url: str = None, *, message: str = None):
        await ctx.message.delete()

        if amount is None or url is None or message is None:
            await ctx.send("❌ Usage: `$webhookspam (amount) (URL) (message)`")
            return

        async with aiohttp.ClientSession() as session:
            for i in range(amount):
                async with session.post(url, json={"content": message}) as resp:
                    if resp.status not in (200, 204):
                        await ctx.send(f"⚠️ Failed to send webhook message #{i+1}. Status code: {resp.status}")
                        return
                await asyncio.sleep(0.1)

        await ctx.send(f"✅ Successfully sent {amount} messages to the webhook!")

async def setup(bot):
    await bot.add_cog(WebhookSpam(bot))
