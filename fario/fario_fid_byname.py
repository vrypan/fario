#!/usr/bin/env python
import os
from dotenv import load_dotenv
from farcaster.HubService import HubService
from farcaster.fcproto.message_pb2 import SignatureScheme, HashScheme, Embed
from farcaster import Message

import argparse

def main():
	parser = argparse.ArgumentParser(prog="fario-fid-byname", description="Get a user's fid")
	parser.add_argument("--hub", help="Use the hub at <ADDRESS>. Ex. --hub 192.168.1.1:2283", type=str)
	parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
	parser.add_argument("username", type=str, help="Cast text")
	args = parser.parse_args()

	load_dotenv()
	# Make sure you check .env.sample to create .env
	hub_address	= args.hub if args.hub else os.getenv("FARCASTER_HUB")

	hub = HubService(hub_address, use_async=False)
	ret  = hub.GetUsernameProof(args.username)

	if args.verbose:
		print(f"User {args.username} is fid {ret.fid}")
	else:
		print(ret.fid)


if __name__ == '__main__':
	main()