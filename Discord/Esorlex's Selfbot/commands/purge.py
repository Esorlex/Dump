import asyncio
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def purge(self, ctx, amount: int):
        await ctx.message.delete()
        if amount < 1 or amount > 150:
            await ctx.send("Please specify a number between 1 and 150.")
            return

        deleted_count = 0

        async for message in ctx.channel.history(limit=amount):
            try:
                await message.delete()
                deleted_count += 1

                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"Error deleting message: {e}")

        await ctx.send(f"Successfully deleted {deleted_count} messages.", delete_after=5)

async def setup(bot):
    await bot.add_cog(Moderation(bot))