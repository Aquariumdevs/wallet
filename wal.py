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
from initialize_wallet import initialize_wallet
from show_keys import show_keys
from delete_wallet import delete_wallet
from initialize_hidden_state import initialize_hidden_state
from sponsor_create_account import sponsor_create_account
from transfer import transfer
from stake import stake
from unstake import unstake
from update_state_hash import update_state_hash
from transfer_with_update_state_hash import transfer_with_update_state_hash
from create_hidden_transaction import create_hidden_transaction, generate_txid
from add_hidden_address import add_hidden_address, derive_hidden_address
from transfer_with_burn_to_stealth import transfer_with_burn_to_stealth
from receive_stealth import receive_stealth
from construct_proofs import construct_proofs
from check_proof_print import check_proof_print
from send_stealth import send_stealth
from show_stealth_addresses import show_stealth_addresses
from show_stealth_balance import show_stealth_balance
from calculate_state_hash import calculate_state_hash


def help():
    print("Usage: wallet.py <command> \n")
    print("Available commands:")
    print("  init                  - Initializes the wallet by creating a new key pair.")
    print("  keys                  - Shows keys and information of the wallet.")
    print("  balance               - Shows the balance of the wallet.")
    print("  delete                - Deletes the local wallet state.")
    print("  create                - Used by a sponsor to create and fund a wallet on the blockchain.")
    print("  transfer              - Transfers funds from the wallet to another address.")
    print("  stake                 - Stakes a specified amount in the wallet.")
    print("  unstake               - Unstakes funds from the blockchain.")
    print("  update                - Updates hidden state hash on the blockchain.")
    print("  send_stealth          - Sends a stealth transaction to another stealth address.")
    print("  receive_stealth       - Receives a stealth transaction from another user.")
    print("  show_stealth_addresses - Shows all stealth addresses associated with the wallet.")
    print("  show_stealth_balance  - Shows the balance of the stealth wallet.")
    print("  transfer_to_stealth   - Transfers and burns transparent funds to stealth balance.")
    print("  help                  - Shows this help message.")
    print("\nFor other commands, they will be passed directly to the low level Go wallet with the provided arguments.")


def interactive():
    state = load_wallet_state()
    if not state or 'secret' not in state or 'address' not in state:
        print("No wallet found. Initializing new wallet...")
        initialize_wallet()
        state = load_wallet_state()  # Reload after initialization

    show_keys()
    show_balance()

    # Check again after initialization attempt
    if 'secret' in state and 'address' in state:
        while True:
            print("\nWallet Operations:")
            print("1. Show Balance")
            print("2. Transfer Funds")
            print("3. Stake Funds")
            print("4. Unstake Funds")
            print("5. Delete Wallet")
            print("6. Fund New Wallet")
            print("7. Initialize Hidden State")
            print("8. Send Stealth Transaction")
            print("9. Receive Stealth Transaction")
            print("10. Show Stealth Addresses")
            print("11. Show Stealth Balance")
            print("12. Transfer to Stealth")
            print("x. Exit")

            choice = input("Select an operation: ").strip()
            if choice == '1':
                show_balance()
            elif choice == '2':
                transfer()
            elif choice == '3':
                stake()
            elif choice == '4':
                unstake()
            elif choice == '5':
                delete_wallet()
                break  # Exiting after deletion as no operations can be performed on a deleted wallet
            elif choice == '6':
                sponsor_create_account()
            elif choice == '7':
                initialize_hidden_state()
            elif choice == '8':
                send_stealth()
            elif choice == '9':
                receive_stealth()
            elif choice == '10':
                show_stealth_addresses()
            elif choice == '11':
                show_stealth_balance()
            elif choice == '12':
                transfer_with_burn_to_stealth()
            elif choice.lower() == 'x':
                print("Exiting wallet application.")
                break
            else:
                print("Invalid choice, please select a valid operation.")
    else:
        print("Wallet initialization failed or was incomplete. Please check and try again.")



def main():
    if len(sys.argv) < 2:
        interactive()
        sys.exit(1)

    function = sys.argv[1]
    args = sys.argv[2:]

    if function == 'init':
        initialize_wallet()
    elif function == 'keys':
        show_keys()
    elif function == 'balance':
        show_balance()
    elif function == 'delete':
        delete_wallet()
    elif function == 'create':
        sponsor_create_account()
    elif function == 'transfer':
        transfer()
    elif function == 'stake':
        stake()
    elif function == 'unstake':
        unstake()
    elif function == 'update':
        update_state_hash()
    elif function == 'send_stealth':
        send_stealth()
    elif function == 'receive_stealth':
        receive_stealth()
    elif function == 'show_stealth_addresses':
        show_stealth_addresses()
    elif function == 'show_stealth_balance':
        show_stealth_balance()
    elif function == 'transfer_to_stealth':
        transfer_with_burn_to_stealth()
    elif function == 'help':
        help()
    else:
        # For other commands, pass them directly to the Go wallet
        output = call_go_wallet(function, args)
        print(output)

if __name__ == "__main__":
    main()





#TODO zk logic
#TODO fix unstake command to not brake the wallet when fail
#TODO batches
#TODO contracts
#TODO security checks
#TODO query for tx success instead of relying to balance... highly unsafe
#TODO wallet backups, recovery and encryption