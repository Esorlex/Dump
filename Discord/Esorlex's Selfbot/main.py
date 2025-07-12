import os
import discord
import aiofiles
import asyncio
from discord.ext import commands
from cryptography.fernet import Fernet
import base64
import hashlib
from colorama import init, Fore
import json

init()

ORANGE = Fore.YELLOW  
RESET = Fore.RESET

KEYS = ["Esorlex'sSelfbotWins", "EsorlexOnTop$", "-Binnut"]

def generate_key(passphrase):
    return base64.urlsafe_b64encode(hashlib.sha256(passphrase.encode()).digest())

FERNET_KEYS = [Fernet(generate_key(key)) for key in KEYS]

def encrypt_token(token):
    encrypted = token.encode()
    for fernet in FERNET_KEYS:
        encrypted = fernet.encrypt(encrypted)
    return encrypted

def decrypt_token(encrypted):
    decrypted = encrypted
    for fernet in reversed(FERNET_KEYS):
        decrypted = fernet.decrypt(decrypted)
    return decrypted.decode()

if not os.path.exists('data'):
    os.makedirs('data')

async def get_or_create_tokens():
    token_path = 'data/tokens.json'
    tokens = []
    if os.path.exists(token_path):
        async with aiofiles.open(token_path, 'r') as file:
            content = await file.read()
            if content:
                data = json.loads(content)
                encrypted_tokens_b64 = data.get("tokens", [])
                for enc_token_b64 in encrypted_tokens_b64:
                    try:
                        encrypted_token = base64.b64decode(enc_token_b64)
                        tokens.append(decrypt_token(encrypted_token))
                    except Exception as e:
                        print(f"{ORANGE}Failed to decrypt a token: {e}{RESET}")

    while True:
        print(f"{ORANGE}Currently stored tokens:{RESET}")
        for i, _ in enumerate(tokens):
            print(f"{ORANGE}  {i+1}. Token #{i+1}{RESET}")
        choice = input(f"{ORANGE}Do you want to add a new token? (y/n): {RESET}").lower()
        if choice != 'y':
            break
        new_token = input(f"{ORANGE}Enter your new Discord token: {RESET}").strip()
        if new_token:
            tokens.append(new_token)

    encrypted_tokens_b64 = []
    for t in tokens:
        encrypted_token = encrypt_token(t)
        encrypted_tokens_b64.append(base64.b64encode(encrypted_token).decode())

    data = {"tokens": encrypted_tokens_b64}
    async with aiofiles.open(token_path, 'w') as file:
        await file.write(json.dumps(data))

    if not tokens:
        print(f"{ORANGE}No tokens available, exiting.{RESET}")
        exit(1)

    print(f"{ORANGE}Select which token to use:{RESET}")
    for i, _ in enumerate(tokens):
        print(f"{ORANGE}  {i+1}. Token #{i+1}{RESET}")

    while True:
        selected = input(f"{ORANGE}Enter token number (1-{len(tokens)}): {RESET}")
        if selected.isdigit():
            idx = int(selected) - 1
            if 0 <= idx < len(tokens):
                return tokens[idx]
        print(f"{ORANGE}Invalid selection, try again.{RESET}")

async def get_or_create_prefix():
    prefix_path = 'data/prefix.json'
    if os.path.exists(prefix_path):
        async with aiofiles.open(prefix_path, 'r') as file:
            content = await file.read()
            if content:
                data = json.loads(content)
                prefix = data.get("prefix")
                if prefix:
                    return prefix.strip()

    prefix = input(f"{ORANGE}Enter your bot prefix: {RESET}")
    data = {"prefix": prefix}
    async with aiofiles.open(prefix_path, 'w') as file:
        await file.write(json.dumps(data))
    return prefix

bot = commands.Bot(command_prefix="$", self_bot=True)

bot.remove_command('help')

async def load_commands():
    if not os.path.exists('commands'):
        os.makedirs('commands')

    for file in os.listdir('commands'):
        if file.endswith('.py'):
            await bot.load_extension(f'commands.{file[:-3]}')

async def load_user_commands():
    if not os.path.exists('user_commands'):
        os.makedirs('user_commands')

    for file in os.listdir('user_commands'):
        if file.endswith('.py'):
            await bot.load_extension(f'user_commands.{file[:-3]}')

@bot.event
async def on_ready():
    print(f"{ORANGE}Logged in as {bot.user}{RESET}")
    await load_commands()
    await load_user_commands()
    print(f"{ORANGE}Commands loaded!{RESET}")
    print(f"{ORANGE}Use your bot's prefix to interact with it.{RESET}")

    bot_username = bot.user.name
    bot_user_id = bot.user.id
    num_servers = len(bot.guilds)
    num_admin_servers = sum(1 for guild in bot.guilds if guild.me.guild_permissions.administrator)

    os.system('cls' if os.name == 'nt' else 'clear')  
    print(f"{ORANGE}Bot Username: {bot_username}{RESET}")
    print(f"{ORANGE}Bot User ID: {bot_user_id}{RESET}")
    print(f"{ORANGE}Number of Servers: {num_servers}{RESET}")
    print(f"{ORANGE}Number of Servers with Administrator: {num_admin_servers}{RESET}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        try:
            await ctx.message.delete()
        except:
            pass

if __name__ == "__main__":
    token = asyncio.run(get_or_create_tokens())
    prefix = asyncio.run(get_or_create_prefix())
    bot.command_prefix = prefix
    bot.run(token)
