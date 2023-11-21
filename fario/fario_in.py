#!/usr/bin/env python
import os
import sys
from time import sleep
from farcaster.HubService import HubService
from farcaster.fcproto.message_pb2 import Message
import base64
import argparse
from . config import get_conf
from . __about__ import version

def main():
	parser = argparse.ArgumentParser(prog="fario-in", description="Send messages to Farcaster hub.")
	parser.add_argument('--version', action='version', version='%(prog)s v'+version)
	parser.add_argument("--hub", help="Use the hub at <HUB>. Ex. --hub 192.168.1.1:2283", type=str)
	parser.add_argument("--ssl", help="Use SSL", action="store_true")
	parser.add_argument("--wait", type=int, help="Wait for <WAIT> milliseconds between message submissions.", default=100)
	args = parser.parse_args()

	conf = get_conf(required=['hub'], args=args)

	hub = HubService(conf['hub'], use_async=False, use_ssl=conf['ssl'])

	for line in sys.stdin:
		m = Message.FromString(base64.b64decode(line))
		r = hub.SubmitMessage(m)
		sleep(args.wait/1000)

if __name__ == '__main__':
	main()