import discord
from discord.ext import commands
import asyncio
import os
import json

class WebhookCreator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_guild_permissions(manage_webhooks=True)
    async def createwebhooks(self, ctx):
        await ctx.message.delete()

        folder = "db"
        filepath = os.path.join(folder, "webhooks.json")

        os.makedirs(folder, exist_ok=True)

        webhook_urls = []

        for channel in ctx.guild.text_channels:
            try:
                webhook = await channel.create_webhook(name="EsorlexWebhook")
                webhook_urls.append({
                    "channel": channel.name,
                    "url": webhook.url
                })
                await asyncio.sleep(1)
            except discord.Forbidden:
                continue
            except Exception as e:
                await ctx.send(f"⚠️ Error creating webhook in #{channel.name}: {e}")

        # Write the webhook URLs to a JSON file
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(webhook_urls, f, indent=4)

        await ctx.send(f"✅ Created {len(webhook_urls)} webhooks and saved to `{filepath}`.")

async def setup(bot):
    await bot.add_cog(WebhookCreator(bot))
