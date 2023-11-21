#!/usr/bin/env python

import sys
import base64
from farcaster.fcproto.message_pb2 import MessageType, Message
from google.protobuf.json_format import MessageToDict, MessageToJson
import argparse
from . __about__ import version

def main():
	parser = argparse.ArgumentParser(prog="fario_grep", 
		description="A utility to read fario records from stdin, and select the ones that match a given string.")
	parser.add_argument("--signer", action='store_true', help="Treat search string as signer public key. Must be in hex starting with '0x'", default=0)
	parser.add_argument("--not-signer", action='store_true', help="Treat search string as signer public key. Match !search_string. Must be in hex starting with '0x'", default=0)
	parser.add_argument("search_string", type=str, help="String to search for")
	parser.add_argument('--version', action='version', version='%(prog)s v'+version)
	args = parser.parse_args()

	for line in sys.stdin:
		m = Message.FromString(base64.b64decode(line))
		if args.signer:
			if m.signer==bytes.fromhex(args.search_string[2:]):
				print(line.strip())
		elif args.not_signer:
			if m.signer!=bytes.fromhex(args.search_string[2:]):
				print(line.strip())
		elif str(m).find(args.search_string) >-1 :
			print(line)

if __name__ == '__main__':
	main()