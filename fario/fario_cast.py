#!/usr/bin/env python
import os
from dotenv import load_dotenv
from farcaster.HubService import HubService
from farcaster.fcproto.message_pb2 import SignatureScheme, HashScheme, Embed
from farcaster import Message
import argparse

def main():
	parser = argparse.ArgumentParser(prog="fario-cast", description="Send a cast from the command line.")
	parser.add_argument("--hub", help="Use the hub at <ADDRESS>. Ex. --hub 192.168.1.1:2283", type=str)
	parser.add_argument("--key", type=str, help="Signer's private key")
	parser.add_argument("--fid", type=int, help="User's fid")
	parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
	parser.add_argument("text", type=str, help="Cast text")
	args = parser.parse_args()

	load_dotenv()
	# Make sure you check .env.sample to create .env
	hub_address	= args.hub if args.hub else os.getenv("FARCASTER_HUB")
	app_signer = args.key if args.key else os.getenv("APP_SIGNER_KEY")
	user_fid = args.fid if args.fid else int( os.getenv("USER_FID") )

	hub = HubService(hub_address, use_async=False)
	message_builder = Message.MessageBuilder(
		HashScheme.HASH_SCHEME_BLAKE3, 
		SignatureScheme.SIGNATURE_SCHEME_ED25519, 
		bytes.fromhex(app_signer[2:])
	)

	data = message_builder.cast.add(
		fid = user_fid, 
		text = args.text[:320]
	)
	msg  = message_builder.message(data)

	ret  = hub.SubmitMessage(msg)
	if args.verbose:
		print(f"Message posted: {args.text[:320]}")

if __name__ == '__main__':
	main()