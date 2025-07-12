from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        await ctx.message.delete()

        commands_list = [cmd.name for cmd in self.bot.commands if not cmd.hidden]

        help_message = (
            "**🛠 Available Commands 🛠**\n\n"
            + "\n".join(f"➡️  `{name}`" for name in commands_list)
            + "\n\nThank you for using Esorlex's Selfbot! We love sus!😍 *(and chatgpt)*\n"
        )

        await ctx.send(help_message)

async def setup(bot):
    await bot.add_cog(Help(bot))