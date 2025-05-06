from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

def create_key(pin, salt):
    return PBKDF2(pin, salt, dkLen=32, count=1000000, hmac_hash_module=SHA256)

def create_salt():
    return get_random_bytes(16)

def create_nonce():
    return get_random_bytes(16)

def create_dummy_data(size):
    return get_random_bytes(size)

def encrypt_data(data, key, nonce, counter):
    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce, initial_value=counter)
    return cipher.encrypt(data)

def decrypt_data(ciphertext, key, nonce, counter):
    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce, initial_value=counter)
    return cipher.decrypt(ciphertext)