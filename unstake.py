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


def unstake():
    state = load_wallet_state()

    # Check if the wallet has been properly initialized
    if not all(key in state for key in ['secret', 'address', 'counter']):
        print("Wallet is not properly initialized.")
        return

    secret = state['secret']
    source = state['address']
    counter = state['counter']

    # Convert the decimal counter to a hexadecimal string
    counter_hex = int_to_hex_str(int(counter))

    try:
        # Increment the local counter for this new transaction
        state['counter'] += 1
        save_wallet_state(state)

        stake_output = call_go_wallet("releaseTx", [secret, source, counter_hex])
        print("Unstaking successful:")
        print(stake_output)
    except Exception as e:
        print(f"Failed to unstake: {e}")

if __name__ == "__main__":
    unstake()

