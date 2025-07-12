import discord
from discord.ext import commands
import aiohttp
import asyncio
import os
import json

WEBHOOK_FILE = "db/webhooks.json"

class MassWebhookSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_webhooks(self):
        os.makedirs(os.path.dirname(WEBHOOK_FILE), exist_ok=True)
        if not os.path.exists(WEBHOOK_FILE):
            with open(WEBHOOK_FILE, 'w') as f:
                json.dump([], f)
            return []
        with open(WEBHOOK_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    @commands.command()
    async def masswebhookspam(self, ctx, amount: int = None, *, message: str = None):
        await ctx.message.delete()

        if amount is None or message is None or amount < 1:
            await ctx.send("❌ Usage: `$masswebhookspam (amount) (message)` and amount must be > 0")
            return

        webhook_data = self.load_webhooks()
        webhook_urls = [entry["url"] for entry in webhook_data if "url" in entry]

        if not webhook_urls:
            await ctx.send("⚠️ No valid webhooks found in the database.")
            return

        success_count = 0

        async with aiohttp.ClientSession() as session:
            tasks = []
            for _ in range(amount):
                for url in webhook_urls:
                    tasks.append(self.send_to_webhook_with_retries(session, url, message))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for res in results:
                if isinstance(res, Exception):
                    pass
                elif res:
                    success_count += 1

        await ctx.send(f"✅ Sent {success_count} messages using stored webhooks.")

    async def send_to_webhook_with_retries(self, session, url, message, max_retries=5):
        retries = 0
        while retries < max_retries:
            try:
                async with session.post(url, json={"content": message}) as resp:
                    if resp.status in (200, 204):
                        return True
                    else:
                        print(f"⚠️ Failed webhook (status {resp.status}): {url}")
            except Exception as e:
                print(f"⚠️ Error sending to webhook {url}: {e}")
            retries += 1

        return False

async def setup(bot):
    await bot.add_cog(MassWebhookSpam(bot))