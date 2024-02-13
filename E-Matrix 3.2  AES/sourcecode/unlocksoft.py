 
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

def unpad(data):
    padding_length = data[-1]
    return data[:-padding_length]

def decrypt_data(encrypted_data, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, base64.b64decode(iv))
    decrypted_data = cipher.decrypt(encrypted_data)
    return unpad(decrypted_data)

def decrypt_file(file_path, key):
    with open(file_path, 'rb') as file:
        encrypted_data = base64.b64decode(file.readline().strip())
        iv = file.readline().strip().decode('utf-8')

    decrypted_data = decrypt_data(encrypted_data, key, iv)

    decrypted_file_path = file_path[:-4]  # Removing the '.enc' extension
    with open(decrypted_file_path, 'wb') as file:
        file.write(decrypted_data)

    os.remove(file_path)  # Remove the encrypted file after decryption

    return decrypted_file_path

def main():
    password = getpass("Enter password: ")
    key = scrypt(password, salt=b'salt', key_len=16, N=2**14, r=8, p=1)

    for file_name in os.listdir('.'):
        if file_name.endswith('.json.enc'):
            decrypted_file_path = decrypt_file(file_name, key)
            print(f"{file_name} decrypted successfully. Decrypted file saved as {decrypted_file_path}")

if __name__ == "__main__":
    main()
