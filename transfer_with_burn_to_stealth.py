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
from calculate_state_hash import calculate_state_hash
from construct_proofs import construct_proofs

def transfer_with_burn_to_stealth():
    state = load_wallet_state()
    if not all(key in state for key in ['secret', 'address', 'counter', 'state_hash']):
        print("Wallet is not properly initialized or missing vital information.")
        return

    state_backup = state

    secret = state['secret']
    source = int_to_hex_str(int(state['address']))

    # This is the burn address; funds sent here are considered 'burnt'
    burn_address = '00000000'  

    amount_input = input("Enter the amount to transfer to stealth: ").strip()
    if not amount_input.isdigit() or int(amount_input) <= 0:
        print("Invalid amount. Please enter a positive integer.")
        return

    amount = int(amount_input)
    if state['balance'] < amount:
        print("Insufficient balance to perform the operation.")
        return

    amount_hex = int_to_hex_str(amount)
    counter_hex = int_to_hex_str(int(state['counter']))
    state_hash = state['state_hash']  # The current state hash before updating

    show_balance()
    state = load_wallet_state()  # Reload state after the operation

    # Adding the burnt amount to the stealth UTXOs
    new_utxo = {'address': source, 'amount': amount}
    state['internal_state']['utxos'].append(new_utxo)
    state['internal_state']['balance'] += amount  # Update the stealth balance

    # Update the internal state hash after adding the new transaction
    new_state_hash = calculate_state_hash(state['internal_state'])
    state['state_hash'] = new_state_hash
    save_wallet_state(state)

    try:
        show_balance()
        state = load_wallet_state()
        prev_balance = state['balance']
        # Sending the transparent funds to be burnt in exchange for stealth funds
        transfer_output = call_go_wallet("transferWithUpdateTx", [secret, source, burn_address, amount_hex, state_hash, counter_hex])
       
        show_balance()
        state = load_wallet_state()  # Reload state after the operation

        if prev_balance == state['balance']:  # Checking if balance was correctly updated
            print("Failed to burn transparent funds. Transaction unsuccessful.")
            save_wallet_state(state_backup)
        else:
            print("Transparent funds successfully burnt. Updating stealth balance.")
            state['counter'] += 1  # Increment the transaction counter

            # Construct a new proof for the updated state
            new_proofs = construct_proofs(state, new_utxo)

            save_wallet_state(state)

            print(f"Stealth balance updated successfully. New state hash: {new_state_hash}")
            print(f"New proofs constructed for the updated state: {new_proofs}")
    except Exception as e:
        print(f"Failed to update state hash: {e}")
        save_wallet_state(state_backup)


if __name__ == "__main__":
    transfer_with_burn_to_stealth()
