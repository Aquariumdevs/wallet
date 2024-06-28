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


def delete_wallet():
    global wallet_state_file  # Ensure the function knows about the global variable
    if os.path.exists(wallet_state_file):
        try:
            os.remove(wallet_state_file)
            print("Wallet file has been successfully deleted.")
        except Exception as e:
            print(f"Failed to delete wallet file: {e}")
    else:
        print("Wallet file does not exist.")

if __name__ == "__main__":
    delete_wallet()
