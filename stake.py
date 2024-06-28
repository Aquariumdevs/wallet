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


def stake():
    state = load_wallet_state()

    # Check if the wallet has been properly initialized
    if not all(key in state for key in ['secret', 'address', 'counter']):
        print("Wallet is not properly initialized.")
        return

    secret = state['secret']
    source = state['address']
    counter = state['counter']

    amount_input = input("Enter the amount to stake: ").strip()
    if not amount_input.isdigit() or int(amount_input) <= 0:
        print("Invalid amount. Please enter a positive integer.")
        return

    # Convert the decimal amount to a hexadecimal string
    amount_hex = int_to_hex_str(int(amount_input))

    # Convert the decimal counter to a hexadecimal string
    counter_hex = int_to_hex_str(int(counter))

    show_balance()
    state = load_wallet_state()
    prev_balance = state['balance']

    try:
        stake_output = call_go_wallet("stakeTx", [secret, source, amount_hex, counter_hex])
        show_balance()
        state = load_wallet_state()
        if prev_balance != state['balance']:
            print("Staking successful!")
            state['counter'] += 1  # Increment the transaction counter
            save_wallet_state(state)
        else:
            print("Unsuccessful operation!")

        #print(stake_output)
    except Exception as e:
        print(f"Failed to stake: {e}")

if __name__ == "__main__":
    stake()

