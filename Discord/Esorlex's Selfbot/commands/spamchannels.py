import discord
from discord.ext import commands
import asyncio

class SpamChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def spamchannels(self, ctx, amount: int = None, *, message: str = None):
        await ctx.message.delete()

        if amount is None or message is None:
            await ctx.send("❌ Usage: `$spamchannels (amount) (message)`")
            return

        text_channels = [ch for ch in ctx.guild.text_channels if ch.permissions_for(ctx.guild.me).send_messages]

        if not text_channels:
            await ctx.send("⚠️ I don't have permission to send messages in any channels.")
            return

        for i in range(amount):
            for channel in text_channels:
                try:
                    await channel.send(message)
                except Exception as e:
                    print(f"⚠️ Could not send to {channel.name}: {e}")
                await asyncio.sleep(0.1)  

        await ctx.send(f"✅ Sent `{message}` to {len(text_channels)} channels, {amount} times.")

async def setup(bot):
    await bot.add_cog(SpamChannels(bot))
