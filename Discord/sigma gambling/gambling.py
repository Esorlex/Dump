import discord
from discord.ext import commands
from discord.ui import Button, View
from discord.ext import commands
import random
import asyncio
import json
import os
import math
from datetime import datetime, timedelta, timezone

autowork_tasks = {}

# Bot setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)
client = discord.Client(intents=intents)

# Economy file
ECONOMY_FILE = 'economy.json'

def load_economy():
    if os.path.exists(ECONOMY_FILE):
        with open(ECONOMY_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_economy(data):
    with open(ECONOMY_FILE, 'w') as f:
        json.dump(data, f, indent=4, default=str)  # Use default=str to handle datetime

def get_user_data(user_id):
    economy = load_economy()
    user_id_str = str(user_id)
    if user_id_str not in economy:
        economy[user_id_str] = {
            'gems': 0,
            'last_work': None,
            'autowork_active': False,
            'last_autowork_stop': None,
            'total_wins': 0,
            'total_losses': 0,
            'daily_wins': 0,
            'daily_losses': 0
        }
        save_economy(economy)
    user_data = economy[user_id_str]
    # Convert last_work and last_autowork_stop from string to datetime if they exist
    if user_data.get('last_work'):
        user_data['last_work'] = datetime.fromisoformat(user_data['last_work']).astimezone(timezone.utc)
    if user_data.get('last_autowork_stop'):
        user_data['last_autowork_stop'] = datetime.fromisoformat(user_data['last_autowork_stop']).astimezone(timezone.utc)
    return user_data

def update_user_data(user_id, key, value):
    economy = load_economy()
    user_id_str = str(user_id)
    if user_id_str not in economy:
        economy[user_id_str] = {
            'gems': 0,
            'last_work': None,
            'autowork_active': False,
            'last_autowork_stop': None,
            'total_wins': 0,
            'total_losses': 0,
            'daily_wins': 0,
            'daily_losses': 0
        }
    # Convert datetime to string if the key is 'last_work' or 'last_autowork_stop'
    if key in ['last_work', 'last_autowork_stop'] and value:
        value = value.astimezone(timezone.utc).isoformat()
    economy[user_id_str][key] = value
    save_economy(economy)

@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)  # 30 seconds cooldown per user
async def work(ctx):
    user_id = ctx.author.id
    user_data = get_user_data(user_id)
    last_work = user_data['last_work']
    now = datetime.now(timezone.utc)

    if last_work and now < last_work + timedelta(seconds=30):
        retry_after = (last_work + timedelta(seconds=30) - now).total_seconds()
        await ctx.send(f"{ctx.author.mention}, you're on cooldown! Please try again in {int(retry_after)} seconds.")
        return
    
    update_user_data(user_id, 'gems', user_data['gems'] + 5)  # Earn 1 gem
    update_user_data(user_id, 'last_work', now)  # Update last work time
    await ctx.send(f"{ctx.author.mention} worked and earned 5 gems!")


@bot.command()
async def richlist(ctx):
    # Load the economy data
    economy = load_economy()

    # Sort users by gems in descending order and get the top 10
    richest = sorted(economy.items(), key=lambda x: x[1]['gems'], reverse=True)[:10]

    # Create the embed to display the rich list
    embed = discord.Embed(title="Top 10 Richest Players", color=discord.Color.gold())

    # Loop through the richest users and add them to the embed
    for idx, (user_id, data) in enumerate(richest, start=1):
        user = await bot.fetch_user(int(user_id))  # Fetch the user by ID
        gems = data['gems']
        embed.add_field(name=f"{idx}. {user.name}", value=f"Gems: {gems}", inline=False)

    # Send the rich list embed
    await ctx.send(embed=embed)

@bot.command()
async def autowork(ctx):
    user_id = ctx.author.id
    user_data = get_user_data(user_id)
    now = datetime.now(timezone.utc)

    # Check if the user is on cooldown for stopping autowork
    if user_data['last_autowork_stop'] and now < user_data['last_autowork_stop'] + timedelta(seconds=10):
        retry_after = (user_data['last_autowork_stop'] + timedelta(seconds=10) - now).total_seconds()
        await ctx.send(f"{ctx.author.mention}, you are on cooldown! Please try again in {int(retry_after)} seconds.")
        return

    if user_data['autowork_active']:
        # Stop autoworking
        user_data['autowork_active'] = False
        update_user_data(user_id, 'autowork_active', False)
        if user_id in autowork_tasks:
            autowork_tasks[user_id].cancel()
            del autowork_tasks[user_id]
        # Update the last stop time
        update_user_data(user_id, 'last_autowork_stop', now)
        await ctx.send(f"{ctx.author.mention} has stopped auto-working!")
    else:
        # Start autoworking
        user_data['autowork_active'] = True
        update_user_data(user_id, 'autowork_active', True)
        autowork_tasks[user_id] = asyncio.create_task(autowork_loop(ctx))
        await ctx.send(f"{ctx.author.mention} has started auto-working!")

@bot.command()
async def flip(ctx, amount: float, side: str):
    user_id = ctx.author.id
    user_data = get_user_data(user_id)
    gems = user_data['gems']
    
    if amount <= 0 or amount > gems:
        await ctx.send("You don't have enough gems to flip or invalid amount.")
        return
    
    result = random.choice(['heads', 'tails'])
    if side not in ['heads', 'tails']:
        await ctx.send("Side must be 'heads' or 'tails'.")
        return

    if result == side:
        winnings = amount
        update_user_data(user_id, 'gems', gems + winnings)
        update_user_data(user_id, 'total_wins', user_data['total_wins'] + winnings)
        update_user_data(user_id, 'daily_wins', user_data['daily_wins'] + winnings)
        await ctx.send(f"You won the coin flip and gained {winnings} gems!")
    else:
        update_user_data(user_id, 'gems', gems - amount)
        update_user_data(user_id, 'total_losses', user_data['total_losses'] + amount)
        update_user_data(user_id, 'daily_losses', user_data['daily_losses'] + amount)
        await ctx.send(f"You lost the coin flip and lost {amount} gems.")

@bot.command()
async def gems(ctx):
    user_id = ctx.author.id
    gems = get_user_data(user_id)['gems']
    await ctx.send(f"{ctx.author.mention} has {gems} gems.")

@bot.command()
async def round(ctx):
    user_id = ctx.author.id
    user_data = get_user_data(user_id)
    gems = user_data['gems']
    rounded_gems = math.ceil(gems)  # Round up to the nearest whole number
    update_user_data(user_id, 'gems', rounded_gems)  # Update balance to rounded value
    await ctx.send(f"{ctx.author.mention} rounded up their gems to {rounded_gems}!")

async def autowork_loop(ctx):
    user_id = ctx.author.id
    channel = ctx.bot.get_channel()  # Fetch the specific channel by ID
    
    while True:
        await asyncio.sleep(60)  # Run every minute
        user_data = get_user_data(user_id)
        
        if user_data['autowork_active']:
            update_user_data(user_id, 'gems', user_data['gems'] + 10)  # Earn 2 gems per minute
            update_user_data(user_id, 'total_wins', user_data['total_wins'] + 10)  # Increment total wins
            update_user_data(user_id, 'daily_wins', user_data['daily_wins'] + 10)  # Increment daily wins
            
            await channel.send(f"{ctx.author.mention} has earned 10 gems from auto-working!")

# Crash game command
@bot.command()
@commands.cooldown(1,3, commands.BucketType.user)  # 30 seconds cooldown per user
async def crash(ctx, amount: float):
    user_id = ctx.author.id
    user_data = get_user_data(user_id)
    gems = user_data['gems']
    
    if amount <= 0 or amount > gems:
        await ctx.send("You don't have enough gems for this crash game or invalid amount.")
        return
    
    # Deduct gems for the crash game
    update_user_data(user_id, 'gems', gems - amount)

    crashed = random.random() < 0.3
    winnings = 0

    if crashed:
        # Player loses the game
        winnings = -amount
        result_message = f"CRASHED! You lost {amount} gems."
        embed_color = discord.Color.red()
        update_user_data(user_id, 'total_losses', user_data['total_losses'] + amount)  # Update total losses
        update_user_data(user_id, 'daily_losses', user_data['daily_losses'] + amount)  # Update daily losses
    else:
        # Player wins the game
        winnings = amount * 2  # Example: double the amount
        result_message = f"You won {winnings:.2f} gems!"
        embed_color = discord.Color.green()
        update_user_data(user_id, 'total_wins', user_data['total_wins'] + winnings)  # Update total wins
        update_user_data(user_id, 'daily_wins', user_data['daily_wins'] + winnings)  # Update daily wins

    # Update user data with the result
    update_user_data(user_id, 'gems', gems + winnings)

    # Create and send the embed message
    embed = discord.Embed(
        title="Crash Game",
        description=result_message,
        color=embed_color
    )
    await ctx.send(embed=embed)

# Read the token from token.txt
with open('token.txt', 'r') as file:
    token = file.read().strip()

# Global error handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        retry_after = int(error.retry_after)
        await ctx.send(f"{ctx.author.mention}, you're on cooldown! Try again in {retry_after} seconds.")
    else:
        await ctx.send(f"An error occurred: {str(error)}")

@bot.command()
async def stats(ctx):
    user_id = ctx.author.id
    user_data = get_user_data(user_id)
    
    gems = user_data['gems']
    total_wins = user_data['total_wins']
    total_losses = user_data['total_losses']
    daily_wins = user_data['daily_wins']
    daily_losses = user_data['daily_losses']
    debt = total_losses - total_wins
    debt_message = f"You are in debt of {debt:.2f} gems." if debt > 0 else "You are not in debt."

    embed = discord.Embed(
        title=f"{ctx.author.name}'s Stats",
        color=discord.Color.blue()  # You can change the color to whatever you like
    )
    embed.add_field(name="Gems", value=f"{gems}", inline=True)
    embed.add_field(name="Total Wins", value=f"{total_wins:.2f} gems", inline=True)
    embed.add_field(name="Total Losses", value=f"{total_losses:.2f} gems", inline=True)
    embed.add_field(name="Daily Wins", value=f"{daily_wins:.2f} gems", inline=True)
    embed.add_field(name="Daily Losses", value=f"{daily_losses:.2f} gems", inline=True)
    embed.add_field(name="Debt Status", value=debt_message, inline=False)

    await ctx.send(embed=embed)

async def end_game(self, interaction: discord.Interaction):
    # Reveal all the bomb positions and disable all buttons
    for item in self.children:
        if isinstance(item, MinesButton):
            item.disabled = True
            if item.index in self.bomb_positions:
                item.style = discord.ButtonStyle.red
                item.label = '💣'
            elif not item.label:
                item.style = discord.ButtonStyle.green
                item.label = '💎'
                
    self.game_ended = True
    
    # Check if interaction has already been responded to
    try:
        await interaction.response.edit_message(view=self)
    except discord.errors.InteractionResponded:
        # If the interaction was already responded to, use the message object to edit it
        await interaction.message.edit(view=self)

class MinesGame(discord.ui.View):
    def __init__(self, ctx, amount, user_id):
        super().__init__(timeout=300)  # 5-minute timeout
        self.ctx = ctx
        self.amount = amount
        self.user_id = user_id
        self.revealed = 0
        self.multiplier = 1.25
        self.current_winnings = amount
        self.bomb_positions = random.sample(range(20), 5)  # 5 bombs placed randomly
        self.game_ended = False

        # Create the buttons with labels
        for i in range(20):
            self.add_item(MinesButton(i, self))

        # Add cashout and cancel buttons
        self.add_item(CashoutButton(self))
        self.add_item(CancelButton(self))

    async def reveal_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.game_ended or interaction.user.id != self.user_id:
            return

        # Disable the button once clicked
        button.disabled = True

        if button.index in self.bomb_positions:
            # Bomb found, end the game
            button.style = discord.ButtonStyle.red
            button.label = '💣'
            await interaction.response.edit_message(content=f"{self.ctx.author.mention} hit a bomb and lost {self.amount} gems!", view=self)
            await self.end_game(interaction)
        else:
            # Gem found, increase winnings and continue
            button.style = discord.ButtonStyle.green
            button.label = '💎'
            self.revealed += 1
            self.current_winnings *= self.multiplier
            await interaction.response.edit_message(content=f"{self.ctx.author.mention} revealed a gem! Current winnings: {self.current_winnings:.2f} gems.", view=self)

    async def cashout(self, interaction: discord.Interaction):
        if self.game_ended or interaction.user.id != self.user_id:
            return

        # Cash out the current winnings
        update_user_data(self.user_id, 'gems', get_user_data(self.user_id)['gems'] + self.current_winnings)
        await interaction.response.edit_message(content=f"{self.ctx.author.mention} cashed out {self.current_winnings:.2f} gems!", view=self)
        await self.end_game(interaction)

    async def cancel(self, interaction: discord.Interaction):
        if self.game_ended or interaction.user.id != self.user_id:
            return

        # Cancel the game and return the original amount
        update_user_data(self.user_id, 'gems', get_user_data(self.user_id)['gems'] + self.amount)
        await interaction.response.edit_message(content=f"{self.ctx.author.mention} canceled the game and got back {self.amount} gems.", view=self)
        await self.end_game(interaction)

    async def end_game(self, interaction: discord.Interaction):
        # Reveal all the bomb positions and disable all buttons
        for item in self.children:
            if isinstance(item, MinesButton):
                item.disabled = True
                if item.index in self.bomb_positions:
                    item.style = discord.ButtonStyle.red
                    item.label = '💣'
                elif not item.label:
                    item.style = discord.ButtonStyle.green
                    item.label = '💎'
        self.game_ended = True
        await interaction.response.edit_message(view=self)

class MinesButton(discord.ui.Button):
    def __init__(self, index, game):
        super().__init__(style=discord.ButtonStyle.gray, label="❔", row=index // 5)  # Add a default label
        self.index = index
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        await self.game.reveal_button(self, interaction)


class CashoutButton(discord.ui.Button):
    def __init__(self, game):
        super().__init__(style=discord.ButtonStyle.green, label='Cashout')
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        await self.game.cashout(interaction)


class CancelButton(discord.ui.Button):
    def __init__(self, game):
        super().__init__(style=discord.ButtonStyle.red, label='Cancel')
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        await self.game.cancel(interaction)


@bot.command()
async def mines(ctx, amount: float):
    user_id = ctx.author.id
    user_data = get_user_data(user_id)
    gems = user_data['gems']

    if amount <= 0 or amount > gems:
        await ctx.send(f"{ctx.author.mention}, you don't have enough gems or the amount is invalid.")
        return

    # Deduct the amount from the user's gems
    update_user_data(user_id, 'gems', gems - amount)

    # Start the mines game with 5 bombs
    view = MinesGame(ctx, amount, user_id)
    await ctx.send(f"{ctx.author.mention} has started a Mines game with {amount} gems and 5 bombs!", view=view)

@bot.command()
async def embed(ctx, message=None, title=None, embed_message=None, footer=None):
    # Create the embed object
    embed = discord.Embed()

    # Set the fields if they are not "null"
    if title and title.lower() != "null":
        embed.title = title

    if embed_message and embed_message.lower() != "null":
        embed.description = embed_message

    if footer and footer.lower() != "null":
        embed.set_footer(text=footer)

    # Send both a message and an embed if "message" is provided and isn't "null"
    if message and message.lower() != "null":
        await ctx.send(message, embed=embed)
    else:
        await ctx.send(embed=embed)

from discord.ext.commands import CheckFailure

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CheckFailure):
        await ctx.send(f"Sorry {ctx.author.mention}, you are not whitelisted to use this command.")
    elif isinstance(error, commands.CommandOnCooldown):
        retry_after = int(error.retry_after)
        await ctx.send(f"{ctx.author.mention}, you're on cooldown! Try again in {retry_after} seconds.")
    else:
        await ctx.send(f"An error occurred: {str(error)}")

@bot.event
async def on_member_join(member):
    # Channel ID where the message will be sent
    channel = bot.get_channel()
    
    if channel is not None:
        # Send a welcome message to the channel
        await channel.send(f"Welcome gambler, be amazed {member.mention}!")
        await channel.send(f"https://tenor.com/view/gamba-xqc-gambling-addict-777-gif-25803752")

@bot.command()
async def give(ctx, amount: int, user: discord.User):
    # Check if the person using the command is authorized
    authorized_ids = []
    if ctx.author.id not in authorized_ids:
        await ctx.send(f"Sorry {ctx.author.mention}, you are not authorized to use this command.")
        return
    
    # Ensure the amount is a positive integer
    if amount <= 0:
        await ctx.send(f"{ctx.author.mention}, the amount must be a positive number.")
        return

    # Fetch the recipient's user data
    user_id = user.id
    user_data = get_user_data(user_id)
    
    # Update the user's gems by adding the specified amount
    update_user_data(user_id, 'gems', user_data['gems'] + amount)
    
    # Confirm the transaction
    await ctx.send(f"{ctx.author.mention} gave {amount} gems to {user.mention}!")

@bot.command()
async def transfer(ctx, member: discord.Member, amount: int):
    # Load the economy data
    economy = load_economy()

    sender_id = str(ctx.author.id)
    receiver_id = str(member.id)

    # Check if sender is trying to transfer to themselves
    if sender_id == receiver_id:
        await ctx.send("You can't transfer gems to yourself!")
        return

    # Check if the sender has an account and enough gems
    if sender_id not in economy:
        await ctx.send("You don't have any gems to transfer!")
        return
    if economy[sender_id]['gems'] < amount:
        await ctx.send(f"You don't have enough gems to transfer. You only have {economy[sender_id]['gems']} gems.")
        return

    # Check if the amount is valid
    if amount <= 0:
        await ctx.send("Please enter a valid amount of gems to transfer.")
        return

    # Deduct gems from sender and add to receiver
    economy[sender_id]['gems'] -= amount
    if receiver_id not in economy:
        economy[receiver_id] = {'gems': 0}  # Create an account for the receiver if they don't have one
    economy[receiver_id]['gems'] += amount

    # Save the updated economy data
    save_economy(economy)

    # Notify both users of the transfer
    await ctx.send(f"Successfully transferred {amount} gems to {member.mention}. You now have {economy[sender_id]['gems']} gems.")
    await member.send(f"You have received {amount} gems from {ctx.author.mention}!")

# Run the bot
bot.run(token)
