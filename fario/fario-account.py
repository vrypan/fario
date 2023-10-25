#!/usr/bin/env python
import os
from dotenv import load_dotenv
from farcaster.HubService import HubService
from farcaster.fcproto.message_pb2 import SignatureScheme, HashScheme, Embed
from farcaster.fcproto.onchain_event_pb2 import OnChainEventType, OnChainEvent
from farcaster import Message
from __about__ import version

import argparse
def get_hub_address(args) -> str:
    load_dotenv()
    hub_address = args.hub if args.hub else os.getenv("FARCASTER_HUB")

    if not hub_address:
        print("Error: [fario-account] No hub address. Use --hub of set FARCASTER_HUB in .env.", file=sys.stderr)
        sys.exit(1)
    return hub_address

def get_names_by_fid(args, fid):
    hub_address = get_hub_address(args)
    hub = HubService(hub_address, use_async=False)
    ret  = hub.GetUserNameProofsByFid(fid, page_size=None)
    return [ (m.name.decode('ascii'), '0x'+m.owner.hex()) for m in ret.proofs ]

def get_addr_by_fid(args, fid):
    hub_address = get_hub_address(args)
    hub = HubService(hub_address, use_async=False)
    ret  = hub.GetIdRegistryOnChainEvent(fid)
    return (
        ret.id_register_event_body.to.hex(), 
        ret.id_register_event_body.recovery_address.hex()
    )
    
def print_account(args, account):
    def _print(key, val, rawdata=False):
        if rawdata:
            print(val, end="\t")
        else:
            print(key.ljust(15),val)
    if args.fid:
        _print('fid',account['fid'], args.raw)
    if args.addr:
        _print('address', '0x'+account['addr'], args.raw)
    if args.recovery:
        _print('recovery', '0x'+account['recovery'], args.raw)
    if args.fname:
        fname = [ n for n in account['names'] if n[0][-4:] !='.eth' ]
        if len(fname)>0:
            _print('fname', fname[0][0], args.raw )
        else:
            _print("fname", '-', args.raw)
    if args.name:
        name = [ n for n in account['names'] if n[0][-4:] =='.eth' ]
        if len(name)>0:
            _print('name', name[0][0], args.raw )
        else:
            _print("name", '-', args.raw)
    print()


def by_fid(args, fid=None):
    account={}
    account['fid'] = fid if fid else args.account_fid

    if args.addr or args.recovery:
        account['addr'], account['recovery'] = get_addr_by_fid(args, account['fid'])
    if args.fname or args.name:
        account['names'] = get_names_by_fid(args, account['fid'])
    print_account(args, account)

def by_name(args):
    hub_address = get_hub_address(args)
    hub = HubService(hub_address, use_async=False)
    ret  = hub.GetUsernameProof(args.name)
    fid = ret.fid
    by_fid(args, fid)

def main():
    parser = argparse.ArgumentParser(prog='fario-account')
    parser.add_argument('--version', action='version', version='%(prog)s v'+version)
    parser.add_argument('--raw', action='store_true', help="Output raw values, tab separated.")
    parser.add_argument("--hub", help="Use the hub at <HUB>. Ex. --hub 192.168.1.1:2283", type=str)
    parser.add_argument("--fid", action='store_true', help="Print fid")
    parser.add_argument("--fname", action='store_true', help="Print fname")
    parser.add_argument("--name", action='store_true', help="Print name")
    parser.add_argument("--addr", action='store_true', help="Print custody address")
    parser.add_argument("--recovery", action='store_true', help="Print recovery address")
    subparser = parser.add_subparsers()

    cmd_addr_by_fid = subparser.add_parser("byfid", description="Get account info using the fid")
    cmd_addr_by_fid.add_argument("account_fid", type=int, help="User's fid.")
    cmd_addr_by_fid.set_defaults(func=by_fid)

    cmd_addr_by_name = subparser.add_parser("byname", description="Get account info using name or fname")
    cmd_addr_by_name.add_argument("name", type=str, help="User's name.")
    cmd_addr_by_name.set_defaults(func=by_name)

    args = parser.parse_args()

    if 'func' in args:
        args.func(args)
    

if __name__ == '__main__':
    main()