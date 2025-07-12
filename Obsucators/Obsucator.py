import base64
import os

def obfuscate_code(code):
    parts = []
    for char in code:
        parts.append(f"chr({ord(char)})")
    return f"exec(''.join([{', '.join(parts)}]))"

def obfuscate_file(file_path):
    try:

        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        print(f"Obfuscating: {file_path}")

        for _ in range(3):  
            code = obfuscate_code(code)

        encoded_code = base64.b64encode(code.encode('utf-8')).decode('utf-8')
        obfuscated_code = f"import base64; exec(base64.b64decode('{encoded_code}').decode('utf-8'))"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(obfuscated_code)

        print(f"Obfuscation complete for: {file_path}")

    except OSError as e:
        print(f"Error occurred while processing {file_path}: {e}")

def obfuscate_folder(folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                obfuscate_file(file_path)

if __name__ == '__main__':
    path = input("Enter the Python file or folder path to obfuscate: ").strip('"')

    if os.path.isdir(path):
        obfuscate_folder(path)
    elif os.path.isfile(path) and path.endswith('.py'):
        obfuscate_file(path)
    else:
        print("Invalid file or folder path. Please provide a valid Python file or directory.")