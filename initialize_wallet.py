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


# Initialize the wallet by creating a key pair and saving the initial state
def initialize_wallet():
    state = load_wallet_state()
    if True: #not state.get('address'):
        print("Creating new key pair...")
        while True:
            source = input("Enter the 4-byte index of the sponsor account: ").strip()
            counter = input("Enter the transaction counter for the sponsor account: ").strip()

            # Validate the input format, assuming 4-byte index and counter should be hexadecimal
            if len(source) != 8 or not all(c in '0123456789abcdefABCDEF' for c in source):
                print("Invalid source index format. It must be an 8-character hexadecimal.")
                continue
            if len(counter) != 8 or not all(c in '0123456789abcdefABCDEF' for c in counter):
                print("Invalid counter format. It must be an 8-character hexadecimal.")
                continue

            try:
                output = call_go_wallet("createKeys", [source, counter])
                keys = output.split()
                # Ensure we correctly map the output to state variables
                state['secret'] = keys[0]
                state['public_key'] = keys[2]
                state['bls_public_key'] = keys[3]
                state['pop'] = keys[4]  # Assuming the fourth element is the Proof of Possession (POP)

                save_wallet_state(state)
                print(f"Wallet initialized with secret key: {state['secret']}")
                print(f"Public Key: {state['public_key']}")
                print(f"BLS Public Key: {state['bls_public_key']}")
                print(f"Proof of Possession: {state['pop']}")
                print(f"Credentials (copy and send the following 3 values to your wallet creator): {state['public_key']} {state['bls_public_key']} {state['pop']}")
                break  # Exit the loop on success
            except Exception as e:
                print(f"Failed to create key pair: {e}")
                print("Please check the input and try again.")

if __name__ == "__main__":
    initialize_wallet()

