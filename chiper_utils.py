from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

def create_key(pin, salt):
    return PBKDF2(pin, salt, dkLen=32, count=1000000, hmac_hash_module=SHA256)

def create_salt():
    return get_random_bytes(16)

def create_iv():
    return get_random_bytes(16)

def encrypt_block_data(data, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(data)

def decrypt_block_data(ciphertext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.decrypt(ciphertext)

def encrypt_block_metadata(data, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return pad(cipher.encrypt(data), AES.block_size)

def decrypt_block_metadata(ciphertext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ciphertext), AES.block_size)