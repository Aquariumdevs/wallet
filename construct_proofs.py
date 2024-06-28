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
from check_proof_print import check_proof_print


def construct_proofs(state, stealth_tx):
    # Combine the address and counter into a single 8-byte string for querying
    counter_hex = int_to_hex_str(int(state['counter']) - 1, 4)  # 4 bytes for the counter
    query_param = state['address'] + counter_hex

    try:
        byte_string = call_go_wallet("query", [query_param])
        # print(byte_string)
        # blockchain_path = ''.join(format(int(b), '02x') for b in bytes_path)
        # Remove the square brackets and split the string into a list of string numbers
        print(f"Length of byte_string {byte_string}: {len(byte_string)}")

        byte_values = byte_string.strip('[]').split()
        # Convert each string number to an integer and then to a byte array
        blockchain_path = bytes([int(b) for b in byte_values])
        # print(blockchain_path)
    except Exception as e:
        # print(f"Failed to query blockchain path: {e}")
        return None

    # Convert the received binary data into a bytes object
    path_bytes = blockchain_path  
    print(f"Length of path_bytes: {len(path_bytes)}")

    # Define the size of a hash (32 bytes for SHA-256)
    hash_size = 32
    offset = 0

    # Extracting the first path
    leafkey1 = path_bytes[offset:offset + 8]
    offset += 8
    leafval1 = path_bytes[offset:offset + hash_size]
    offset += hash_size

    root1 = path_bytes[offset:offset + hash_size]
    offset += hash_size

    out1, length = check_proof_print(leafkey1, leafval1, root1, path_bytes[offset:])
    offset += length

    # Extracting the second path
    leafkey2 = path_bytes[offset:offset + 8]
    offset += 8
    leafval2 = path_bytes[offset:offset + hash_size]
    offset += hash_size
    root2 = path_bytes[offset:offset + hash_size]
    offset += hash_size

    out2, _ = check_proof_print(leafkey2, leafval2, root2, path_bytes[offset:])
    out3 = root1 == leafval2




    # print("leafval1:", list(leafval1))
    # print("root1:", list(root1))
    # print("leafkey2:", list(leafkey2))
    # print("leafval2:", list(leafval2))
    # print("root2:", list(root2))




    # print(f"Leaves and paths unpacked. Block height: {block_height}")
    print(f"Constructing proofs for transaction {stealth_tx} with blockchain paths")
    print(out1, out2, out3)

    return str(base64.b64encode(blockchain_path))
