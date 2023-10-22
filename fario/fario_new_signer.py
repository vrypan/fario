#!/usr/bin/env python

import os
from dotenv import load_dotenv
from farcaster.Signer import Signer
import argparse

def main():
	load_dotenv()
	provider	= os.getenv("OP_ETH_PROVIDER") # "Your OP ETH provider endpoint"
	user_fid 	= os.getenv("USER_FID") # "User fid that will approve the signer"
	user_key 	= os.getenv("USER_PRIVATE_KEY") # "User's private key."
	app_fid 	= os.getenv("APP_FID") # "Application fid that will issue the signer."
	app_key 	= os.getenv("APP_PRIVATE_KEY") # "Application's private key"

	
	parser = argparse.ArgumentParser(prog="fario-new-signer", description="Create a new signer")
	parser.add_argument("--provider", help="OP Eth provider endpoint")
	parser.add_argument("--user_fid", help="User's fid.")
	parser.add_argument("--user_key", help="User's private key in hex.")
	parser.add_argument("--app_fid", help="Application's fid.")
	parser.add_argument("--app_key", help="Application's private key in hex.")
	args = parser.parse_args()

	provider = args.provider if args.provider else provider
	user_fid = args.user_fid if args.user_fid else user_fid
	user_key = args.user_key if args.user_key else user_key
	app_fid = args.app_fid if args.app_fid else app_fid
	app_key = args.app_key if args.app_key else app_key

	if not (provider and user_fid and user_key and app_fid and app_key):
		print('Missing parameters. Either define them in .env or as an option.')
		sys.exit(1)

	s = Signer( provider, int(user_fid), user_key, int(app_fid), app_key )

	tx_hash = s.approve_signer()
	signer_private_key = s.key
	signer_public_key = s.signer_pub()

	print(f"=== New Signer approved =====================")
	print(f"Tx: {tx_hash}")
	print(f"User Fid: {user_fid}")
	print(f"App Fid: {user_fid}")
	print(f"Signer public key: 0x{s.signer_pub().hex()}")
	print(f"Signer private key: {s.key.hex()}")
	print(f"=== MAKE SURE YOU SAVE THE PRIVATE KEY!!! ===")

if __name__ == '__main__':
	main()