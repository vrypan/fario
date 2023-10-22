#!/usr/bin/env python
import os
import sys
from time import sleep
from dotenv import load_dotenv
from farcaster.HubService import HubService
from farcaster.fcproto.message_pb2 import Message

import base64
import argparse

def main():
	parser = argparse.ArgumentParser(prog="fario-in", description="Send messages to Farcaster hub.")
	parser.add_argument("--hub", help="Use the hub at <ADDRESS>. Ex. --hub 192.168.1.1:2283", type=str)
	parser.add_argument("--wait", type=int, help="Wait for <WAIT> milliseconds between message submissions.", default=100)
	args = parser.parse_args()

	load_dotenv()
	hub_address = args.hub if args.hub else os.getenv("FARCASTER_HUB")

	if not hub_address:
		print("No hub address. Use --hub of set FARCASTER_HUB in .env.")
		sys.exit(1)

	hub = HubService(hub_address, use_async=False)

	for line in sys.stdin:
		m = Message.FromString(base64.b64decode(line))
		r = hub.SubmitMessage(m)
		sleep(args.wait/1000)

if __name__ == '__main__':
	main()