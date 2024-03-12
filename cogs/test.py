import discord
from discord.ext import commands

class test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @discord.command(description='nocostamrobi')
    async def ping(self, ctx):
        await ctx.respond(f"ping = {self.bot.latency}")

def setup(bot):
    bot.add_cog(test(bot))