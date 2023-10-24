#!/usr/bin/env python
import os
import sys
from time import sleep
from dotenv import load_dotenv
from farcaster.HubService import HubService
from farcaster.fcproto.message_pb2 import MessageType, Message

import base64
import argparse

def get_data(method, fid, page_size, limit, wait):
	first_run=True
	page_token=None
	count = 0
	while (page_token or first_run) and count<limit:
		first_run=False
		casts = method(fid, page_size=100, page_token=page_token)
		for cast in casts.messages:
			out = base64.b64encode(cast.SerializeToString()).decode('ascii')
			yield out
			count +=1
			if count==limit:
				break
		page_token = casts.next_page_token
		sleep(wait)

def get_reactions(method, fid, reaction_type, page_size, limit, wait):
	first_run=True
	page_token=None
	count = 0
	while (page_token or first_run) and count<limit:
		first_run=False
		casts = method(fid=fid, reaction_type=reaction_type, page_size=100, page_token=page_token)
		for cast in casts.messages:
			out = base64.b64encode(cast.SerializeToString()).decode('ascii')
			yield out
			count +=1
			if count==limit:
				break
		page_token = casts.next_page_token
		sleep(wait)

def main():		
	parser = argparse.ArgumentParser(prog="fario-out", description="Export Farcaster data.")
	parser.add_argument("fid", type=int, help="FID")
	parser.add_argument("--casts", help="User casts", action="store_true")
	parser.add_argument("--links", help="User links", action="store_true")
	parser.add_argument("--recasts", help="User recasts", action="store_true")
	parser.add_argument("--likes", help="User likes", action="store_true")
	parser.add_argument("--inlinks", help="Inbound links for user", action="store_true")
	parser.add_argument("--profile", help="User profile data", action="store_true")
	parser.add_argument("--all", help="Equivalent to --casts --links --recasts --likes --profile", action="store_true")
	parser.add_argument("--limit", type=int, help="Number of records. If more than one types of data are exported, the limit applies to each one separately.", default=sys.maxsize)
	parser.add_argument("--hub", help="Use the hub at <HUB>. Ex. --hub 192.168.1.1:2283", type=str)
	parser.add_argument("--wait", type=int, help="Wait for <WAIT> milliseconds between reads.", default=0)
	args = parser.parse_args()

	load_dotenv()
	hub_address = args.hub if args.hub else os.getenv("FARCASTER_HUB")

	if not hub_address:
		print("No hub address. Use --hub of set FARCASTER_HUB in .env.")
		sys.exit(1)

	hub = HubService(hub_address, use_async=False)

	if args.casts or args.all:
		for c in get_data(hub.GetCastsByFid, args.fid, 100, args.limit, args.wait):
			print(c)
	if args.links or args.all:
		for c in get_data(hub.GetLinksByTarget, args.fid, 100, args.limit, args.wait):
			print(c)
	if args.likes or args.all:
		for c in get_reactions(hub.GetReactionsByFid, args.fid, 1, 100, args.limit, args.wait):
			print(c)
	if args.recasts or args.all:
		for c in get_reactions(hub.GetReactionsByFid, args.fid, 2, 100, args.limit, args.wait):
			print(c)
	if args.profile or args.all:
		for c in get_data(hub.GetUserDataByFid, args.fid, 100, args.limit, args.wait):
			print(c)
	if args.inlinks:
		for c in get_data(hub.GetLinksByTarget, args.fid, 100, args.limit, args.wait):
			print(c)
	

if __name__ == '__main__':
	main()