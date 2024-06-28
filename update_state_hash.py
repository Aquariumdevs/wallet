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


def update_state_hash():
    state = load_wallet_state()
    if not all(key in state for key in ['secret', 'address', 'counter', 'state_hash']):
        print("Wallet is not properly initialized or missing vital information.")
        return

    secret = state['secret']
    state_hash = state['state_hash']  # Assume this is calculated elsewhere
    counter_hex = int_to_hex_str(int(state['counter']))
    source = int_to_hex_str(int(state['address']))

    show_balance()
    state = load_wallet_state()
    prev_balance = state['balance']

    try:
        update_output = call_go_wallet("UpdateTx", [secret, source, state_hash, counter_hex])
        show_balance()
        state = load_wallet_state()
        if prev_balance != state['balance']:
            print("Update successful!")
            state['counter'] += 1  # Increment the transaction counter
            save_wallet_state(state)
        else:
            print("Unsuccessful operation!")
    except Exception as e:
        print(f"Failed to update state hash: {e}")
