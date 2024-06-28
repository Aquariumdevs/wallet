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


def derive_hidden_address(public_key, seed, index):
    data_to_hash = f"{public_key}{seed}{index}"
    hidden_address = hashlib.sha256(data_to_hash.encode()).hexdigest()
    return hidden_address


def add_hidden_address(state):
    # Assuming we have a number of hidden addresses already derived
    num_hidden_addresses = len(state['internal_state']['hidden_addresses'])
    public_key = state['public_key']
    private_key_seed = state['secret']  # Using the secret as the seed for derivation

    # Derive a new hidden address
    new_hidden_address = derive_hidden_address(public_key, private_key_seed, num_hidden_addresses)
    
    # Add the new hidden address to the internal state
    state['internal_state']['hidden_addresses'].append(new_hidden_address)

    # Save the updated state
    save_wallet_state(state)

    return new_hidden_address

