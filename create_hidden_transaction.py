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


def create_hidden_transaction(inputs, outputs):
    txid = generate_txid(inputs, outputs)  # Generate a unique ID for the transaction
    return {
        'txid': txid,
        'inputs': inputs,
        'outputs': outputs
    }

def generate_txid(inputs, outputs):
    data = json.dumps({'inputs': inputs, 'outputs': outputs}, sort_keys=True)
    return hashlib.sha256(data.encode()).hexdigest()
