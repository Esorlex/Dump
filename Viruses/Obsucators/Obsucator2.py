import base64
import os

def obfuscate_file(file_path: str):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        print(f"[+] Obfuscating with base64: {file_path}")

        encoded = base64.b64encode(code.encode('utf-8')).decode('utf-8')
        wrapped = (
            "import base64\n"
            f"exec(base64.b64decode('{encoded}').decode('utf-8'))"
        )

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(wrapped)

        print(f"[✓] Obfuscation complete: {file_path}\n")

    except Exception as e:
        print(f"[!] Error with {file_path}: {e}")

def obfuscate_folder(folder_path: str):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.py'):
                obfuscate_file(os.path.join(root, file))

if __name__ == "__main__":
    path = input("Enter the Python file or folder path to obfuscate: ").strip('"')

    if os.path.isdir(path):
        obfuscate_folder(path)
    elif os.path.isfile(path) and path.endswith('.py'):
        obfuscate_file(path)
    else:
        print("[!] Invalid path. Please enter a valid .py file or folder.")
