#!/usr/bin/env python

import os
import json

from web3 import Web3
from eth_account import Account

from dotenv import load_dotenv
from farcaster.Signer import removeSigner
import argparse

def main():
	load_dotenv()

	parser = argparse.ArgumentParser(prog="fario-remove-signer", description="Remove signer")
	parser.add_argument("--provider", help="OP Eth provider endpoint")
	parser.add_argument("--user_key", help="User's private key in hex.")
	parser.add_argument("signer", help="Signer's public key in hex.")
	args = parser.parse_args()

	provider = args.provider if args.provider else os.getenv("OP_ETH_PROVIDER")
	user_key = args.user_key if args.user_key else os.getenv("USER_PRIVATE_KEY")

	if not (provider and user_key and args.signer):
		print('Missing parameters. Either define them in .env or as an option.')
		sys.exit(1)
		
	tx = removeSigner(provider, user_key, args.signer)
	print(f"Signer {args.signer} removed. Tx={tx}")

if __name__ == '__main__':
	main()