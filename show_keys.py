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

# Function to display the wallet keys
def show_keys():
    state = load_wallet_state()

    print("Wallet Information:")
    print(f"Secret Key: {state.get('secret', 'Not Available')}")
    print(f"Public Key: {state.get('public_key', 'Not Available')}")
    print(f"BLS Public Key: {state.get('bls_public_key', 'Not Available')}")

if __name__ == "__main__":
    show_keys()
