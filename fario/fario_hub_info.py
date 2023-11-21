#!/usr/bin/env python
from farcaster.HubService import HubService
from . config import get_conf
from . __about__ import version

import argparse

def get_hub_info():
	parser = argparse.ArgumentParser(prog="fario-hubinfo", description="Show a hub's information.")
	parser.add_argument('--version', action='version', version='%(prog)s v'+version)
	parser.add_argument("--hub", help="Use the hub at <ADDRESS>. Ex. --hub 192.168.1.1:2283", type=str)
	parser.add_argument("--ssl", help="Use SSL", action="store_true")
	args = parser.parse_args()

	conf = get_conf(required=['hub'], args=args)

	hub = HubService(conf['hub'], use_async=False, use_ssl=conf['ssl'])
	ret  = hub.GetInfo()
	print('address:', conf['hub'])
	print(ret)

if __name__ == '__main__':
	get_hub_info()