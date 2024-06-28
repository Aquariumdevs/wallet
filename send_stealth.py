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
from calculate_state_hash import calculate_state_hash
from show_balance import show_balance
from construct_proofs import construct_proofs

def is_utxo_included(address, amount, utxos):
    print(f"Checking for UTXO with address {address} and amount {amount}...")
    for utxo in utxos:
        print(f"Comparing with UTXO {utxo['address']} amount {utxo['amount']}")
        if utxo['address'] == address and utxo['amount'] == amount:
            print("Match found.")
            return True
    print("No match found.")
    return False

def send_stealth():
    state = load_wallet_state()
    to_address_hex = input("Enter the stealth address (hex) to send to: ").strip()
    amount = int(input("Enter the amount to send: ").strip())
    
    state_backup = state
 
    if state['internal_state']['balance'] < amount:
        print("Insufficient balance to perform the stealth transaction.")
        return

    stealth_tx = {'address': to_address_hex, 'amount': amount}
    previous_state_hash = state['state_hash']

    if is_utxo_included(stealth_tx['address'], stealth_tx['amount'], state['internal_state']['hidden_output_txs']):
        print("The stealth transaction is already included in the state. Try with another stealth address or amount.")
        return
    else:
        print("The UTXO is not included in the state.")

    state['internal_state']['hidden_output_txs'].append(stealth_tx)
    state['internal_state']['balance'] -= amount
    new_state_hash = calculate_state_hash(state['internal_state'])

    save_wallet_state(state)

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

            state = load_wallet_state()


            proofs = construct_proofs(state, stealth_tx)
            # Generate the transaction hex that will be sent to the receiver
            transaction_data = {'utxo': stealth_tx, 'proofs': proofs}
            transaction_hex = json.dumps(transaction_data).encode().hex()
    
            state['state_hash'] = new_state_hash
            save_wallet_state(state)
            print(f"Transaction hex to send: {transaction_hex}")

        else:
            print("Unsuccessful operation!")
            save_wallet_state(state_backup)
    except Exception as e:
        print(f"Failed to update state hash: {e}")
        save_wallet_state(state_backup)

if __name__ == "__main__":
    send_stealth()

          