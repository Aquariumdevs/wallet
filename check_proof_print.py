#!/usr/bin/env python3
import subprocess
import json
import sys
import os
import hashlib
import requests
import math
import struct
import base64

from common import load_wallet_state, save_wallet_state, call_go_wallet, get_block_hash, int_to_hex_str
from show_balance import show_balance

HASH_LEN = 32  

def unpack_siblings(b):
    if len(b) < 1:
        raise ValueError("Input is too short to contain the number of steps.")
 
    num_steps = b[0]  # First byte is the number of steps

    expected_len = num_steps * HASH_LEN + 1

    if len(b) < expected_len:
        raise ValueError(f"expected len: {expected_len}, current len: {len(b)}")
    siblings = []
    for i in range(num_steps):
        offset = 1 + i * 2 * HASH_LEN
        left = b[offset:offset + HASH_LEN]
        right = b[offset + HASH_LEN:offset + 2 * HASH_LEN]
        siblings.append((left, right))
    
    return siblings, expected_len

'''
HASH_LEN = hashlib.sha256().digest_size

def unpack_siblings(b):
    full_len = struct.unpack_from('<H', b, 0)[0]
    l = struct.unpack_from('<H', b, 2)[0]
    if len(b) < full_len:
        raise ValueError(f"expected len: {full_len}, current len: {len(b)}")

    bitmap_bytes = b[4:4 + l]
    bitmap = bytes_to_bitmap(bitmap_bytes)
    siblings_bytes = b[4 + l:full_len]
    i_sibl = 0
    empty_sibl = bytes(HASH_LEN)
    siblings = []
    for i in range(len(bitmap)):
        if i_sibl >= len(siblings_bytes):
            break
        if bitmap[i]:
            siblings.append(siblings_bytes[i_sibl:i_sibl + HASH_LEN])
            # print("sibling:", list(siblings_bytes[i_sibl:i_sibl + HASH_LEN]))
            i_sibl += HASH_LEN
        else:
            siblings.append(empty_sibl)
            # print("sibling:", list(empty_sibl))
    return siblings, full_len
'''


def new_intermediate(l, r):
    if len(l) > 255:
        raise ValueError(f"Left key length is too long")
    # b = bytes([2, len(l)]) + l + r
    # hasher = hashlib.sha256()
    # hasher.update(l + r)
    key = l # hasher.digest()
    #print("IM:", list(key))
    return key, r # b


def get_path(num_levels, k):
    path = []
    for n in range(num_levels):
        byte_index = n // 8
        bit_index = n % 8
        byte_value = k[byte_index]
        bit_value = (byte_value & (1 << bit_index)) != 0
        path.append(bit_value)
    return path


def new_leaf_value(k, v):
    if len(k) > 255 or len(v) > 65535:
        raise ValueError(f"Key or value length is too long")
    hasher = hashlib.sha256()
    hasher.update(k + v + bytes([1]))
    leaf_key = hasher.digest()
    # print("k:", list(k))
    # print("v:", list(v))
    # print("lk:", list(leaf_key))

    leaf_value = bytes([1, len(k)]) + k + v
    # print("lv:", list(leaf_value))
    return leaf_key, leaf_value



def check_proof_print(k, v, root, packed_siblings):

    siblings, length = unpack_siblings(packed_siblings)

    key_path = bytearray(math.ceil(len(siblings) / 8))
    key_path[:len(k)] = k

    key, _ = new_leaf_value(k, v)
    # print("key:", list(key))

    path = get_path(len(siblings), key_path)
    for i in reversed(range(len(siblings))):
        if path[i]:
            key, _ = new_intermediate(siblings[i], key)
            # print("L:", list(key))
        else:
            key, _ = new_intermediate(key, siblings[i])
            # print("R:", list(key))

    if key == root:
        print("success")
        return True, length
    else:
        print("FAIL")
        return False, length
