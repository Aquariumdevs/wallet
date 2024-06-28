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


def show_stealth_addresses():
    state = load_wallet_state()
    hidden_addresses = state['internal_state'].get('hidden_addresses', [])

    if hidden_addresses:
        print("Stealth Addresses:")
        for index, address in enumerate(hidden_addresses, 1):
            print(f"{index}. {address}")
    else:
        print("No stealth addresses found.")

if __name__ == "__main__":
    show_stealth_addresses()
