#!/usr/bin/env python
from farcaster.HubService import HubService
from farcaster.fcproto.message_pb2 import SignatureScheme, HashScheme, Embed
from farcaster import Message
from . config import get_conf
from . __about__ import version

import argparse

def main():
	parser = argparse.ArgumentParser(prog="fario-fid-byname", description="Get a user's fid")
	parser.add_argument('--version', action='version', version='%(prog)s v'+version)
	parser.add_argument("--hub", help="Use the hub at <ADDRESS>. Ex. --hub 192.168.1.1:2283", type=str)
	parser.add_argument("--ssl", help="Use SSL", action="store_true")
	parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
	parser.add_argument("username", type=str, help="Cast text")
	args = parser.parse_args()

	conf = get_conf(required=['hub'], args=args)

	hub = HubService(conf['hub'], use_async=False, use_ssl=conf['ssl'])
	ret  = hub.GetUsernameProof(args.username)

	if args.verbose:
		print(f"User {args.username} is fid {ret.fid}")
	else:
		print(ret.fid)


if __name__ == '__main__':
	main()