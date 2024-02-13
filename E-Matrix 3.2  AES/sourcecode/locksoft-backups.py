import os
import json
import base64
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
from getpass import getpass
from shutil import copyfile
from datetime import datetime

def pad(data):
    padding_length = AES.block_size - len(data) % AES.block_size
    return data + bytes([padding_length] * padding_length)

def encrypt_file(file_path, key):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    plaintext = json.dumps(data).encode('utf-8')
    plaintext = pad(plaintext)

    cipher = AES.new(key, AES.MODE_CBC)
    iv = base64.b64encode(cipher.iv).decode('utf-8')

    ciphertext = cipher.encrypt(plaintext)

    encrypted_file_path = file_path + '.enc'
    with open(encrypted_file_path, 'wb') as file:
        file.write(base64.b64encode(ciphertext))
        file.write(b'\n')
        file.write(iv.encode('utf-8'))

    os.remove(file_path)  # Remove the source file after encryption

    return encrypted_file_path

def create_backup(encrypted_file_path):
    original_filename = encrypted_file_path[:-4]  # Remove the '.enc' extension
    backup_filename = f"{original_filename}-backup-{datetime.now().strftime('%Y%m%d%H%M%S')}.enc"
    copyfile(encrypted_file_path, backup_filename)
    print(f"Backup created for {original_filename} as {backup_filename}")

def main():
    password = getpass("Enter password: ")
    key = scrypt(password, salt=b'salt', key_len=16, N=2**14, r=8, p=1)

    for file_name in os.listdir('.'):
        if file_name.endswith('.json'):
            encrypted_file_path = encrypt_file(file_name, key)
            print(f"{file_name} encrypted successfully. Encrypted file saved as {encrypted_file_path}")
            create_backup(encrypted_file_path)

if __name__ == "__main__":
    main()
