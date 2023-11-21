#!/usr/bin/env python

import sys
import base64
from farcaster.HubService import HubService
from farcaster.fcproto.message_pb2 import MessageType, Message
from farcaster import FARCASTER_EPOCH
from google.protobuf.json_format import MessageToDict, MessageToJson
import argparse
from datetime import datetime
from termcolor import colored
import textwrap
from . config import get_conf
# from . __about__ import version

def pp_date(t: int) -> str:
	ret = '(' + datetime.fromtimestamp(t+FARCASTER_EPOCH).strftime('%Y-%m-%d %H:%M:%S') + ')'
	return colored( ret, 'light_grey')
def pp_link(l: str) -> str:
	return "\n> " + colored(l.strip(), "blue", attrs=['underline'])
def pp_cast_id(m: Message) -> str:
	out = colored(f"@{m.data.fid}", "green", attrs=["bold"])
	out += colored(f"/{m.hash.hex()} ", 'green')
	out += colored(
		datetime.fromtimestamp(m.data.timestamp+FARCASTER_EPOCH).strftime('%Y-%m-%d %H:%M:%S'),
		"light_grey"
		)
	return out
def pp_out(t: str) -> str:
	lines = t.split('\n')
	ret = '\n'.join([ "| "+l for l in lines ])
	return ret
def pp_fid(fid: int) -> str:
	return colored(f"@{fid}", "magenta", attrs=["bold"]) 

def pp_cast(m: Message, child_text='') -> str:
	# wrapper = textwrap.TextWrapper(width=70)
	assert m.data.type == MessageType.MESSAGE_TYPE_CAST_ADD, 'Not a CAST_ADD message'
	out = ""
	
	out += 	pp_cast_id(m) + "\n"

	text = m.data.cast_add_body.text
	if hasattr(m.data.cast_add_body, 'mentions_positions'):
		offset = 0
		for i in range(len(m.data.cast_add_body.mentions)):
			pos = m.data.cast_add_body.mentions_positions[i]+offset
			username = f"{pp_fid(m.data.cast_add_body.mentions[i])}"
			text = text[0:pos] + username + text[pos:]
			offset += len(username)
	out += "\n".join([ "\n".join(textwrap.wrap(l, width=70)) for l in text.splitlines() ])
	# out += "\n".join(textwrap.wrap(text, width=70))
	if hasattr(m.data.cast_add_body, 'embeds'):
		for embed in m.data.cast_add_body.embeds:
			if hasattr(embed,'url'):
				out += pp_link(embed.url)
	out = textwrap.indent(out, '| ')
	if m.data.cast_add_body.parent_cast_id.fid:
		out = f'↳ In reply to {m.data.cast_add_body.parent_cast_id.fid}/{m.data.cast_add_body.parent_cast_id.hash.hex()}\n' + out
	return out

def main():
	parser = argparse.ArgumentParser(prog="fario-pprint", description="Convert fario export to human-friendly output")
	#parser.add_argument("--lines", type=int, help="Only parse first <LINES>", default=0)
	parser.add_argument("--limit", type=int, help="Number of records. If more than one types of data are exported, the limit applies to each one separately.", default=sys.maxsize)
	# parser.add_argument('--version', action='version', version='%(prog)s v'+version)
	parser.add_argument("fid", type=int, help="Export messages from fid=FID")
	args = parser.parse_args()

	conf = get_conf(required=['hub'], args=args)
	hub = HubService(conf['hub'], use_async=False)
	ret = hub.GetCastsByFid(args.fid, 10)

	count=0
	for m in ret.messages:
		#m = Message.FromString(base64.b64decode(line))
		if m.data.type == MessageType.MESSAGE_TYPE_CAST_ADD:
			out = pp_cast(m)
		else:
			out = None
		
		if out:
			print()
			print(out)

		if args.limit and count >= args.limit:
			break

if __name__ == '__main__':
	main()