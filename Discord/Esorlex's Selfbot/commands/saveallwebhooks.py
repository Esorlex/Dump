import discord
from discord.ext import commands
import os
import json
import asyncio

WEBHOOK_FILE = "db/webhooks.json"

class SaveWebhooks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def save_webhooks(self, webhook_list):
        os.makedirs(os.path.dirname(WEBHOOK_FILE), exist_ok=True)
        with open(WEBHOOK_FILE, 'w', encoding='utf-8') as f:
            json.dump(webhook_list, f, indent=4)

    async def safe_send(self, ctx, content, max_retries=5):
        retries = 0
        while retries < max_retries:
            try:
                await ctx.send(content)
                return
            except discord.HTTPException as e:
                wait_time = 2 ** retries  
                print(f"Send failed (retry {retries + 1}/{max_retries}): {e}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                retries += 1
        print("❌ Failed to send message after several retries.")

    @commands.command()
    async def saveallwebhooks(self, ctx):
        await ctx.message.delete()
        webhook_list = []

        for channel in ctx.guild.text_channels:
            try:
                webhooks = await channel.webhooks()
                for webhook in webhooks:
                    webhook_list.append({
                        "id": webhook.id,
                        "name": webhook.name,
                        "channel_id": webhook.channel.id,
                        "url": webhook.url
                    })
            except discord.Forbidden:
                print(f"⚠️ Missing permissions to fetch webhooks for {channel.name}")
            except Exception as e:
                print(f"⚠️ Error fetching webhooks from {channel.name}: {e}")

        self.save_webhooks(webhook_list)

        await self.safe_send(ctx, f"✅ Saved {len(webhook_list)} webhooks to `{WEBHOOK_FILE}`.")

async def setup(bot):
    await bot.add_cog(SaveWebhooks(bot))