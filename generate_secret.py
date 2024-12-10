import os
import binascii

def generate_secret_key(length=24):
    return binascii.hexlify(os.urandom(length)).decode()

# Generate a 24-byte secret key
secret_key = generate_secret_key()
print(f"Your secret key: {secret_key}")