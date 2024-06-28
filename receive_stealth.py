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
from check_proof_print import check_proof_print
from construct_proofs import construct_proofs
from send_stealth import is_utxo_included
from calculate_state_hash import calculate_state_hash

def verify_proofs(proof, block_height, stealth_tx):
    hash = get_block_hash(block_height)
    # Simulate proof verification with public inputs and blockchain path
    verify_merkle_proofs(proof)
    print(f"Verifying proof {proof} for transaction {stealth_tx} against blockchain state hash {hash} ")
    return True  # Placeholder result

def verify_merkle_proofs(proof):
    path_bytes = base64.b64decode(proof)
    # Define the size of a hash (32 bytes for SHA-256)
    hash_size = 32
    offset = 0

    # Extracting the first path
    leafkey1 = path_bytes[offset:offset + 8]
    offset += 8
    leafval1 = path_bytes[offset:offset + hash_size]
    offset += hash_size
    root1 = path_bytes[offset:offset + hash_size]
    offset += hash_size
    out1, length = check_proof_print(leafkey1, leafval1, root1, path_bytes[offset:])
    offset += length

    # Extracting the second path
    leafkey2 = path_bytes[offset:offset + 8]
    offset += 8
    leafval2 = path_bytes[offset:offset + hash_size]
    offset += hash_size
    root2 = path_bytes[offset:offset + hash_size]
    offset += hash_size
    out2, _ = check_proof_print(leafkey2, leafval2, root2, path_bytes[offset:])
    out3 = root1 == leafval2
    retrieved = get_block_hash(int.from_bytes(leafkey2, 'big')+1)
    binary_string = bytes.fromhex(retrieved)
    out4 = root2 == binary_string[32:]



    print("leafkey1:", list(leafkey1))
    print("leafval1:", list(leafval1))
    print("root1:", list(root1))
    print("leafkey2:", list(leafkey2))
    print("leafval2:", list(leafval2))
    print("root2:", list(root2))


    print("retrieved:", list(binary_string))

    # print(f"Leaves and paths unpacked. Block height: {block_height}")
    print(f"Verified proofs for blockchain paths:")
    print(out1, out2, out3, out4)

    if out1 & out2 & out3 & out4:
        return True
    return False


def receive_stealth():
    state = load_wallet_state()
    transaction_hex = input("Enter the transaction hex you received: ").strip()
    transaction_data = json.loads(bytes.fromhex(transaction_hex).decode())
    stealth_tx = transaction_data['utxo']
    proofs = (transaction_data['proofs'])[2:-1]

    if is_utxo_included(transaction_data['utxo']['address'], transaction_data['utxo']['amount'], state['internal_state']['utxos']):
        print("The UTXO is already included in the state.")
        return
    else:
        print("The UTXO is not included in the state.")
  
    blockchain_height = 1  # This would typically come from the proof analysis
    if verify_proofs(proofs, blockchain_height, stealth_tx):
        print("Proof verified successfully.")
   
        # Update the internal state with the received transaction
        state['internal_state']['utxos'].append(stealth_tx)
        state['internal_state']['balance'] += stealth_tx['amount']

        # Construct a new proof for the updated state
        new_state_hash = calculate_state_hash(state['internal_state'])
        state['state_hash'] = new_state_hash

        new_proofs = construct_proofs(state, stealth_tx)

        save_wallet_state(state)
        print(f"State updated successfully. New state hash: {new_state_hash}")
        print(f"New proofs constructed for the updated state: {new_proofs}")
    else:
        print("Proof verification failed.")

if __name__ == "__main__":
    receive_stealth()

