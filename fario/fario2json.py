#!/usr/bin/env python

import sys
import base64
from farcaster.fcproto.message_pb2 import MessageType, Message
from google.protobuf.json_format import MessageToDict, MessageToJson
import argparse
from . __about__ import version

def main():
	parser = argparse.ArgumentParser(prog="fario2json", description="Convert fario export to json")
	parser.add_argument("--lines", type=int, help="Only parse first <LINES>", default=0)
	parser.add_argument('--version', action='version', version='%(prog)s v'+version)
	args = parser.parse_args()

	print("[")
	separator = ''
	count=0
	for line in sys.stdin:
		m = Message.FromString(base64.b64decode(line))
		out = MessageToJson(m)
		print(separator+str(out))
		if not separator:
			separator = ', '
		if args.lines and count >= args.lines:
			break
			
	print("]")

if __name__ == '__main__':
	main()