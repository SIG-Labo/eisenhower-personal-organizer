 
"""
Eisenhower-Matrix Personal Planner 3.0
Copyright (c) 2024 Peter De Ceuster
https://peterdeceuster.uk/
Free to distribute
Distributed under the FPA General Code License
"""


import os
import json
import base64
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
from getpass import getpass

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

def main():
    password = getpass("Enter password: ")
    key = scrypt(password, salt=b'salt', key_len=16, N=2**14, r=8, p=1)

    for file_name in os.listdir('.'):
        if file_name.endswith('.json'):
            encrypted_file_path = encrypt_file(file_name, key)
            print(f"{file_name} encrypted successfully. Encrypted file saved as {encrypted_file_path}")

if __name__ == "__main__":
    main()
