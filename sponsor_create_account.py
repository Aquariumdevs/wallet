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

def sponsor_create_account():
    # Load the sponsor's wallet state and verify its initialization
    state = load_wallet_state()
    required_keys = ['secret', 'address', 'counter']
    if not all(key in state and state[key] for key in required_keys):
        print("Sponsor's wallet is not properly initialized or missing vital information.")
        return

    print("Enter the Credentials: output from the wallet initialization of the wallet to be sponsored:")
    init_output = input().strip().split()
    if len(init_output) < 3:
        print("Invalid input. The initialization output should contain at least 3 elements.")
        return

    # Extracting new wallet's public key, BLS public key, and POP from the input
    spubkey, blspk, pop = init_output[0], init_output[1], init_output[2]
    print("!!!",len(spubkey), len(blspk), len(pop))
    amount_input = input("Enter the amount to fund the new wallet: ").strip()
    if not amount_input.isdigit() or int(amount_input) <= 0:
        print("Invalid amount. Please enter a positive integer.")
        return

    # Convert the decimal amount to a hexadecimal string
    amount_hex = int_to_hex_str(int(amount_input))

    # Sponsor's secret and other details
    secret_sponsor = state['secret']
    source = state['address']
    counter = int_to_hex_str(int(state['counter']))  # Assuming counter is large, adjust byte size as needed

    show_balance()
    state = load_wallet_state()
    prev_balance = state['balance']

    try:
        account_creation_output = call_go_wallet(
            "createAccountTx",
            [secret_sponsor, spubkey, blspk, pop, source, amount_hex, counter]
        )
        show_balance()
        state = load_wallet_state()
        if prev_balance != state['balance']:
            print("Account creation successful!")
            state['counter'] += 1  # Increment the transaction counter
            save_wallet_state(state)
        else:
            print("Unsuccessful operation!")

        #print(account_creation_output)

        save_wallet_state(state)  # Save the updated state
    except Exception as e:
        print(f"Failed to create account: {e}")

if __name__ == "__main__":
    sponsor_create_account()

