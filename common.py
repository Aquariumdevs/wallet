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



def get_block_hash(height, tendermint_node_address="http://localhost:26657"):
    """
    Get the block hash for a given block height from a Tendermint node.

    :param height: The block height to query for.
    :param tendermint_node_address: The address of the Tendermint node (default is 'http://localhost:26657').
    :return: The block hash as a string if successful, None otherwise.
    """
    # Construct the URL for querying the block
    url = f"{tendermint_node_address}/block?height={height}"

    try:
        # Make the HTTP request to the Tendermint node
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            block_data = response.json()

            # Extract the block hash
            block_hash = block_data['result']['block']['header']['app_hash']

            return block_hash
        else:
            print(f"Failed to fetch block data: HTTP {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error fetching block data: {e}")
        return None

# Path to the wallet state file
wallet_state_file = 'wallet_state.json'

# Function to convert integer to a hexadecimal string with proper zero padding
def int_to_hex_str(integer_value, byte_size=4):
    hex_str = format(integer_value, f'0{byte_size * 2}x')  # Multiplied by 2 for hex digit pair per byte
    return hex_str

# Function to load the wallet state from a file
def load_wallet_state():
    default_internal_state = {
        'prev_state_hash': '',
        'hidden_addresses': [],
        'hidden_input_txs': [],
        'hidden_output_txs': [],
        'balance': 0  # Internal balance separate from the public balance
    }
    default_state = {
        'address': '',
        'secret': '',
        'counter': 0,
        'balance': 0,  # Public balance
        'internal_state': default_internal_state,
        'state_hash': ''
    }
    if os.path.exists(wallet_state_file):
        with open(wallet_state_file, 'r') as file:
            state = json.load(file)
            state['internal_state'] = {**default_internal_state, **state.get('internal_state', {})}
            return {**default_state, **state}
    return default_state


# Function to save the wallet state to a file
def save_wallet_state(state):
    with open(wallet_state_file, 'w') as file:
        json.dump(state, file)

# Call the Go wallet command
def call_go_wallet(command, args):
    go_command = ["./wallet", command] + args
    output = []  # List to capture the output lines
    try:
        # Use Popen for real-time output
        with subprocess.Popen(go_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as process:
            for line in process.stdout:
                #print(line, end='')  # Print output line by line in real-time
                output.append(line.strip())  # Add line to output list
            process.wait()  # Wait for the subprocess to finish
            if process.returncode != 0:
                raise Exception(f"Error executing command '{command}' with return code {process.returncode}")
    except Exception as e:
        print(f"Failed to execute command '{command}': {e}")
        sys.exit(1)
    
    return '\n'.join(output)  # Return the captured output as a single string


def bytes_to_bitmap(bitmap_bytes):
    """Convert bitmap bytes to a list of boolean values."""
    bitmap = []
    if len(bitmap_bytes) == 0:
        bitmap_bytes = bytearray(8)

    for byte in bitmap_bytes:
        for i in range(8):
            # Shift bit and check if it's set
            bitmap.append(bool(byte & (1 << i) > 0))
    return bitmap