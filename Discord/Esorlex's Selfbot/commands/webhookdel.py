import discord
from discord.ext import commands
import requests
from colorama import Fore

class WebhookDelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def webhookdel(self, ctx, webhook_url: str = None):
        await ctx.message.delete()

        if webhook_url is None:
            await ctx.send(Fore.RED + "❌ Please provide a webhook URL to delete.")
            return

        try:
            response = requests.delete(webhook_url)
            if response.status_code == 204:
                await ctx.send("✅ Webhook successfully deleted!")
            else:
                await ctx.send(f"⚠️ Failed to delete webhook. Status code: {response.status_code}")
        except Exception as e:
            await ctx.send(f"⚠️ Error deleting webhook: {e}")

async def setup(bot):
    await bot.add_cog(WebhookDelete(bot))
