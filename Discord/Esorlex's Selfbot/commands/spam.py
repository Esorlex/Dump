from discord.ext import commands

class Spam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def spam(self, ctx, amount: int, *, message: str):
        await ctx.message.delete()

        if amount <= 0:
            await ctx.send("Please provide a number greater than 0 for the spam count.")
            return

        for _ in range(amount):
            await ctx.send(message)

async def setup(bot):
    await bot.add_cog(Spam(bot))