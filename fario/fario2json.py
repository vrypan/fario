#!/usr/bin/env python
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from farcaster.HubService import HubService
from farcaster.fcproto.message_pb2 import MessageType, Message
import json
FARCASTER_EPOCH = 1609459200  # January 1, 2021 UTC

import base64
from fario.protobuf_to_dict import protobuf_to_dict

import argparse

def main():
	parser = argparse.ArgumentParser(prog="fario2json", description="Convert fario export to json")
	parser.add_argument("--lines", type=int, help="Only parse first <LINES>", default=0)
	args = parser.parse_args()

	print("[")
	separator = ''
	count=0
	for line in sys.stdin:
		m = Message.FromString(base64.b64decode(line))
		out = json.dumps(protobuf_to_dict(m))
		print(separator+str(out))
		if not separator:
			separator = ', '
		if args.lines and count >= args.lines:
			break
			
	print("]")

if __name__ == '__main__':
	main()