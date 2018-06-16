# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/21/2018


import base64
from Crypto.Cipher import AES
from hashlib import sha1

key = '123456'


def add_to_16(value):
    while len(value) % 16 != 0:
        value += '\0'
    return str.encode(value)  # return bytes


def do_encrypt(text):
    aes = AES.new(add_to_16(key), AES.MODE_ECB)
    encrypt_aes = aes.encrypt(add_to_16(text))
    try:  # python3
        encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # return bytes
    except:  # python2
        encrypted_text = str(base64.b64encode(encrypt_aes))  # return bytes
    return encrypted_text


def do_decrypt(text):
    aes = AES.new(add_to_16(key), AES.MODE_ECB)
    try:  # python3
        base64_decrypted = base64.decodebytes(text.encode(encoding='utf-8'))
        decrypted_text = str(aes.decrypt(base64_decrypted), encoding='utf-8')  # return str
    except:  # python2
        base64_decrypted = base64.b64decode(text.encode(encoding='utf-8'))
        decrypted_text = str(aes.decrypt(base64_decrypted))  # return str
    return decrypted_text.replace('\0', '')


def do_hash(text):
    sha = sha1()
    sha.update(text.encode('utf8'))
    result = sha.hexdigest()
    return result


if __name__ == '__main__':
    encrypt_text = do_encrypt('john_password')
    print(encrypt_text)
    print(do_decrypt(encrypt_text))
    print(do_hash('john_password'))
    print(do_hash(''))
