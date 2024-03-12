import discord
from discord.ext import tasks, commands
import json
import random
from emoji import *

intents = discord.Intents.default()
intents.messages = True
intents.typing = False
intents.presences = False

try:
    with open('user_data.json', 'r') as file:
        user_data = json.load(file)
except FileNotFoundError:
    user_data = {}
    
def save_user_data():
    with open('user_data.json', 'w') as file:
        json.dump(user_data, file, indent=4)
        
class levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldown_users = set()
        self.xp_task.start()
        
    def get_user_level_info(self, user_id):
        user_id = str(user_id)
        if user_id in user_data:
            return user_data[user_id]
        else:
            return {'level': 1, 'xp': 0}
        
    def cog_unload(self):
        self.xp_task.cancel()
        
    @tasks.loop(seconds=30)
    async def xp_task(self):
        for user_id in self.cooldown_users.copy():
            self.cooldown_users.remove(user_id)
            
    @xp_task.before_loop
    async def before_xp_task(self):
        await self.bot.wait_until_ready()
        
    @commands.Cog.listener()
    async def on_message(self, message):
        guild_id = 1038037955836661840
        
        if message.author.bot or not message.guild:
            return
        if message.guild.id != guild_id:
            return
        
        user_id = str(message.author.id)
        
        if user_id in self.cooldown_users:
            return
        
        if user_id not in user_data:
            user_data[user_id] = {'xp': 0, 'level': 1}
            
        user_data[user_id]['xp'] += random.randrange(5, 26)
        
        if user_data[user_id]['xp'] >= user_data[user_id]['level'] * 100:
            user_data[user_id]['level'] += 1
            level = user_data[user_id]['level']
            
            if level >= 5:
                role_id = 1153058242474283178
                role = message.guild.get_role(role_id)
                await message.author.add_roles(role)
                
            if level >= 15:
                role_id = 1153059143133966446
                role = message.guild.get_role(role_id)
                await message.author.add_roles(role)
                
            if level >= 30:
                role_id = 1153059645770965053
                role = message.guild.get_role(role_id)
                await message.author.add_roles(role)
                
            if level >= 50:
                role_id = 1153059990496616599
                role = message.guild.get_role(role_id)
                await message.author.add_roles(role)
                
            user_data[user_id]['xp'] = 0
            await message.channel.send(f'{message.author.mention} Gratuluję zdobycia {level} poziomu!')
            
        save_user_data()
        self.cooldown_users.add(user_id)
        
    @discord.slash_command(description='Sprawdź swój poziom na serwerze.')
    async def poziom(self, ctx, user: discord.User = None):
        user = user or ctx.author
        user_id = str(user.id)
        
        if user_id in user_data:
            level = user_data[user_id]['level']
            xp = user_data[user_id]['xp']
            xp_needed = level * 100
            progress = xp / xp_needed
            
            progress_bar = "["
            filled = int(20 * progress)
            progress_bar += "█" * filled
            progress_bar += " " * (20 - filled)
            progress_bar += f"] {int(progress * 100)}%"
            
            xp_emoji = discord.PartialEmoji(animated=True, name="xp", id="1170497037339476018")
            level_emoji = discord.PartialEmoji(animated=True, name='lvl', id='1170499855068696717')
            progress_emoji = discord.PartialEmoji(animated=True, name='prg', id='1170499275306827826')
            
            embed = discord.Embed(
                title=f'Karta postępu użytkownika @{user.display_name}',
                color=0xa751ed
                )
            embed.add_field(name=f'{level_emoji} Poziom:', value=level, inline=True)
            embed.add_field(name=f'{xp_emoji} XP:', value=f'{xp}/{xp_needed}', inline=True)
            embed.add_field(name=f'{progress_emoji} Postęp:', value=progress_bar, inline=False)
            embed.set_thumbnail(url=user.display_avatar.url)
            
            await ctx.respond(embed=embed)
        else:
            await ctx.respond('Użytkownik nie został znaleziony w bazie.')
            
    @discord.slash_command(description='Top 10 na serwerze!')
    async def ranking(self, ctx):
        sorted_users = sorted(user_data.items(), key=lambda x: x[1]['level'], reverse=True)
        
        xp_emoji = discord.PartialEmoji(animated=True, name="xp", id="1170497037339476018")
        lb_emoji = discord.PartialEmoji(animated=True, name="troph1", id='1170686245576392814')
        level_emoji = discord.PartialEmoji(animated=True, name='lvl', id='1170499855068696717')
        position_emoji = discord.PartialEmoji(animated=True, name="qmark", id="1170695514854006874")
        embed = discord.Embed(title=f"{lb_emoji} Leaderboard:", color=0xffe45c)
        
        for index, (user_id, data) in enumerate(sorted_users[:10], start=1):
            try:
                user = await self.bot.fetch_user(int(user_id))
                embed.add_field(
                    name=f"{index}. {user.display_name}",
                    value=f"{level_emoji}Level: {data['level']}\n"
                    f"{xp_emoji}XP: {data['xp']}",
                    inline=False
                    )
            except discord.errors.NotFound:
                await ctx.respond(f'{failed_emoji} Użytkownik nie znajduje się w bazie danych!')
                
        embed.add_field(
                name="========================================",
                value="",
                inline=False
            )
        
        author_id = str(ctx.author.id)
        author_position = next((index for index, (user_id, _) in enumerate(sorted_users) if user_id == author_id), None)
        if author_position is not None:
            embed.add_field(
                name=f"{position_emoji}Twoja pozycja: " + f"{author_position + 1}.",
                value="",
                inline=False
            )
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1155238879041962047/1170684183836897362/image.png?ex=6559ef9b&is=65477a9b&hm=0a3d0aec66ffe074ffa819d15e6e5d0beb2778d089ea180fdf54b6ba427821b3&")

        await ctx.respond(embed=embed)
        
    @discord.slash_command()
    async def dodajxp(self, ctx, user: discord.User, xp_amount: int):
        
        user_id = str(user.id)
        if user_id in user_data:
            user_data[user_id]['xp'] += xp_amount
            save_user_data()
            await ctx.respond(f"{success_emoji}Dodano {xp_amount} XP użytkownikowi {user.mention}")
        else:
            await ctx.respond(f"{failed_emoji}Użytkownik nie został znaleziony w bazie.")
           
def setup(bot):
    bot.add_cog(levels(bot))