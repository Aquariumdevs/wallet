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


# Function to display the wallet balance
def show_balance():
    state = load_wallet_state()

    address = state.get('address')
    if not address:
        print("Local Address Index: Not Available - Attempting to retrieve from blockchain...")
        if 'bls_public_key' in state:
            try:
                output = call_go_wallet("query", [state['bls_public_key']])
                address_bytes = output.strip('[]').split()
                if len(address_bytes) == 4:
                    # Convert from list of byte values to hex string
                    address = ''.join(format(int(b), '02x') for b in address_bytes)
                    # Update state with new address
                    state['address'] = address
                    save_wallet_state(state)
                    print(f"Retrieved 4-byte Address Index: {address}")
                else:
                    print("The wallet is not yet on-chain or there's a connection issue.")
                    return
            except Exception as e:
                print(f"Failed to query on-chain information: {e}")
                return
        else:
            print("BLS Public Key not found. Please initialize the wallet.")
            return

    # Query for balance using the 4-byte address
    try:
        balance_output = call_go_wallet("query", [address])
        balance_bytes = balance_output.strip('[]').split()
        if len(balance_bytes) > 4:
            # Decode the big-endian 4-byte address to a single numerical value
            balance = int(''.join(format(int(b), '02x') for b in balance_bytes[:4]), 16)
            state['balance'] = balance
            save_wallet_state(state)
            print(f"Balance: {balance}")
        else:
            print("Failed to retrieve a valid balance. The response format is incorrect.")
    except Exception as e:
        print(f"Failed to query balance information: {e}")

if __name__ == "__main__":
    show_balance()

