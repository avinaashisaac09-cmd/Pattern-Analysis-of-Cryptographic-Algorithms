import time
import os
import pymysql
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

# Database connection
conn = psycopg2.connect(
    dbname="encryption_db",
    user="postgres",
    password="avinash27",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS encryption_times (
        id SERIAL PRIMARY KEY,
        method VARCHAR(10),
        encryption_time FLOAT,
        decryption_time FLOAT
    )
''')
conn.commit()

# AES Encryption and Decryption
def aes_encrypt_decrypt(plaintext, key):
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    decryptor = cipher.decryptor()

    while len(plaintext) % 16 != 0:
        plaintext += b"SHE IS A DECEMBER FLOWER WHICH BLOOMED IN NOVEMBER"

    start_time = time.time()
    encrypted_data = encryptor.update(plaintext) + encryptor.finalize()
    encryption_time = time.time() - start_time

    start_time = time.time()
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    decryption_time = time.time() - start_time

    return encryption_time, decryption_time

# RSA Encryption and Decryption
def rsa_encrypt_decrypt(plaintext, private_key, public_key):
    start_time = time.time()
    encrypted_data = public_key.encrypt(
        plaintext.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    encryption_time = time.time() - start_time

    start_time = time.time()
    decrypted_data = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    decryption_time = time.time() - start_time

    return encryption_time, decryption_time

# Example usage
plaintext = b"HER NAME IS LOTUS"
key = os.urandom(16)  # AES key

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
public_key = private_key.public_key()

# AES encryption/decryption timing
aes_encryption_time, aes_decryption_time = aes_encrypt_decrypt(plaintext, key)

# RSA encryption/decryption timing
rsa_encryption_time, rsa_decryption_time = rsa_encrypt_decrypt(plaintext.decode('utf-8'), private_key, public_key)

# Store results in PostgreSQL
def store_results(method, encryption_time, decryption_time):
    cursor.execute(
        "INSERT INTO encryption_times (method, encryption_time, decryption_time) VALUES (%s, %s, %s)",
        (method, encryption_time, decryption_time)
    )
    conn.commit()

store_results("AES", aes_encryption_time, aes_decryption_time)
store_results("RSA", rsa_encryption_time, rsa_decryption_time)

# Print results
print(f"AES Encryption Time: {aes_encryption_time:.6f} seconds")
print(f"AES Decryption Time: {aes_decryption_time:.6f} seconds")
print(f"RSA Encryption Time: {rsa_encryption_time:.6f} seconds")
print(f"RSA Decryption Time: {rsa_decryption_time:.6f} seconds")

# Close connection
cursor.close()
conn.close()
