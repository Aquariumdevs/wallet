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

def show_stealth_balance():
    state = load_wallet_state()
    stealth_balance = state['internal_state'].get('balance', 0)

    print(f"Stealth Balance: {stealth_balance}")

if __name__ == "__main__":
    show_stealth_balance()
