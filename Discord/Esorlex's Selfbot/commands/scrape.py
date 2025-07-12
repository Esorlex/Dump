import discord
from discord.ext import commands
import asyncio
import os

class Scrape(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def scrape(self, ctx):
        await ctx.message.delete()
        if not ctx.guild:
            return

        members = await ctx.guild.fetch_members()  
        member_ids = [str(member.id) for member in members]

        os.makedirs("db", exist_ok=True)

        chunk_size = 1000
        filename = "db/scraped.txt"  

        for i in range(0, len(member_ids), chunk_size):
            chunk = member_ids[i:i + chunk_size]

            with open(filename, "a") as f:
                f.write("\n".join(chunk) + "\n")

            await asyncio.sleep(0.5)

        await ctx.send(f"Scraped {len(members)} member IDs and saved to '{filename}'.")

async def setup(bot):
    await bot.add_cog(Scrape(bot))