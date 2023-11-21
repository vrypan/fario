#!/usr/bin/env python

import sys
import base64
from farcaster.fcproto.message_pb2 import MessageType, Message
from google.protobuf.json_format import ParseDict
import argparse
import json
from . __about__ import version

def json2fario():
	parser = argparse.ArgumentParser(prog="json2fario", description="Json to fario. Expects an array of Message in json format.")
	parser.add_argument('--version', action='version', version='%(prog)s v'+version)
	args = parser.parse_args()

	j = json.loads(sys.stdin.read())
	for msg in j:
		pb = ParseDict(msg, Message()) 
		out = base64.b64encode(pb.SerializeToString()).decode('ascii')
		print(out)
		
if __name__ == '__main__':
	json2fario()