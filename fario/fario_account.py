#!/usr/bin/env python
import os
import sys
from datetime import datetime
#from dotenv import load_dotenv
from eth_account import Account
from farcaster.HubService import HubService
from farcaster.fcproto.message_pb2 import SignatureScheme, HashScheme, Embed
from farcaster.fcproto.onchain_event_pb2 import OnChainEventType, OnChainEvent
from farcaster.fcproto.request_response_pb2 import StoreType
from farcaster import FARCASTER_EPOCH
from farcaster import Message
from . __about__ import version
from . config import get_conf, check_conf

import argparse

CONF = {}

def get_hub_address(args) -> str:
    check_conf(CONF, ['hub'])
    hub_address = CONF['hub']
    return hub_address

def get_usage(fid, args):
    def count(c, fn, args):
        ret = fn(**args)
        if hasattr(ret,'messages'):
            c = c + len(ret.messages)
        if hasattr(ret,'proofs'):
            c = c + len(ret.proofs)
        if getattr(ret,'next_page_token', None):
            args['page_token'] = ret.next_page_token
            return( count(c, fn, args) )
        else:
            return c
    hub_address = get_hub_address(args)
    hub = HubService(hub_address, use_async=False, CONF['ssl'])
    usage = (
        ('casts', hub.GetCastsByFid, {"fid":fid, "page_size":1000} ),
        ('links', hub.GetLinksByFid, {"fid":fid, "page_size":1000} ),
        ('likes', hub.GetReactionsByFid, {"fid":fid, "reaction_type":1, "page_size":1000} ),
        ('recasts', hub.GetReactionsByFid, {"fid":fid, "reaction_type":2, "page_size":1000} ),
        ('user_data', hub.GetUserDataByFid, {"fid":fid, "page_size":1000} ),
        ('proofs', hub.GetUserNameProofsByFid, {"fid":fid, "page_size":1000} ),
        ('verifications', hub.GetVerificationsByFid, {"fid":fid, "page_size":1000} )
        )
    usage_counts = {}
    for u in usage:
        usage_counts[u[0]] = count(0, u[1], u[2])
    return usage_counts

def get_names_by_fid(args, fid):
    hub_address = get_hub_address(args)
    hub = HubService(hub_address, use_async=False, CONF['ssl'])
    ret  = hub.GetUserNameProofsByFid(fid, page_size=None)
    return [ (m.name.decode('ascii'), '0x'+m.owner.hex()) for m in ret.proofs ]

def get_addr_by_fid(args, fid):
    hub_address = get_hub_address(args)
    hub = HubService(hub_address, use_async=False, CONF['ssl'])
    ret  = hub.GetIdRegistryOnChainEvent(fid)
    return (
        ret.id_register_event_body.to.hex(), 
        ret.id_register_event_body.recovery_address.hex()
    )
def get_storage_rent_by_fid(args, fid):
    storage=[]
    hub_address = get_hub_address(args)
    hub = HubService(hub_address, use_async=False, CONF['ssl'])
    ret  = hub.GetOnChainEvents(fid=fid, event_type=4, page_size=None)
    return [
        (e.storage_rent_event_body.units,
        e.storage_rent_event_body.expiry,
        e.storage_rent_event_body.payer.hex())
        for e in ret.events
    ]
    
def get_storage_limits_by_fid(args, fid):
    hub_address = get_hub_address(args)
    hub = HubService(hub_address, use_async=False, CONF['ssl'])
    ret  = hub.GetCurrentStorageLimitsByFid(fid)
    limits = { StoreType.Name(l.store_type)[11:].lower(): l.limit for l in ret.limits }
    return (limits)
    
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
    if args.storage_rent:
        if not args.raw:
            print("\nStorage Units Rented")
            print("====================")
            _print("Units", "Date                Paid by", False)
        for s in account['storage_rent']:
            timestamp = datetime.fromtimestamp(s[1]+FARCASTER_EPOCH).strftime('%Y-%m-%dT%H:%M:%S')
            _print(str(s[0]), f"{timestamp} 0x{s[2]}", args.raw)
    if args.storage_limits:
        if not args.raw:
            print("\nCurrent Storage Limits")
            print("======================")
        for l in account['storage_limits']:
            _print(l, account['storage_limits'][l], args.raw)
    if args.storage_usage:
        if not args.raw:
            print("\nCurrent Usage")
            print("=============")
        for l in account['storage_usage']:
            _print(l, account['storage_usage'][l], args.raw)
    print()


def by_fid(args, fid=None):
    account={}
    account['fid'] = fid if fid else args.account_fid

    if args.all:
        args.addr = True
        args.fname = True
        args.storage_rent = True
        args.storage_limits = True 
        args.storage_usage = True 

    if args.addr or args.recovery:
        account['addr'], account['recovery'] = get_addr_by_fid(args, account['fid'])
    if args.fname or args.name:
        account['names'] = get_names_by_fid(args, account['fid'])
    if args.storage_rent:
        account['storage_rent']=get_storage_rent_by_fid(args, account['fid'])
    if args.storage_limits:
        account['storage_limits'] = get_storage_limits_by_fid(args, account['fid'])
    if args.storage_usage:
        account['storage_usage'] = get_usage(account['fid'], args)
    print_account(args, account)

def by_name(args):
    hub_address = get_hub_address(args)
    hub = HubService(hub_address, use_async=False, CONF['ssl'])
    ret  = hub.GetUsernameProof(args.name)
    fid = ret.fid
    by_fid(args, fid)

def from_secret(args):
    print(  "=== DANGER!!! ===")
    print(  "Revealing your secret phrase (seed or mnemonic) to someone, gives\n"
            "them full control over your Farcaster account, including the ability\n"
            "to move your fid to an other wallet!\n\n"
            "This script will calculate your privet key using your secret phrase.\n"
            "This script runs locally and does not send ANY data to any third party.\n\n"
            "Do your own research before trusting anyone with your account's key\n"
            "or mnemonic. This includes this script too.\n\n"
    )
    seed = input("Enter secret phrase: ")
    if seed.strip():
        Account.enable_unaudited_hdwallet_features()
        acc = Account.from_mnemonic(seed)
        print("Account key:".ljust(15), acc.key.hex())
        print("Account addr:".ljust(15), f"0x{acc.address}")
    
def main():
    parser = argparse.ArgumentParser(prog='fario-account')
    parser.add_argument('--version', action='version', version='%(prog)s v'+version)
    parser.add_argument('--raw', action='store_true', help="Output raw values, tab separated.")
    parser.add_argument("--hub", help="Use the hub at <HUB>. Ex. --hub 192.168.1.1:2283", type=str)
    parser.add_argument("--ssl", help="Use SSL", action="store_true")
    parser.add_argument("--fid", action='store_true', help="Print fid")
    parser.add_argument("--fname", action='store_true', help="Print fname")
    parser.add_argument("--name", action='store_true', help="Print name")
    parser.add_argument("--addr", action='store_true', help="Print custody address")
    parser.add_argument("--storage-rent", action='store_true', help="Print storage rent events")
    parser.add_argument("--storage-limits", action='store_true', help="Print storage limits")
    parser.add_argument("--storage-usage", action='store_true', help="Print storage usage")
    parser.add_argument("--recovery", action='store_true', help="Print recovery address")
    parser.add_argument("--all", action='store_true', help="Print all available information")
    subparser = parser.add_subparsers()

    cmd_addr_by_fid = subparser.add_parser("byfid", description="Get account info using the fid")
    cmd_addr_by_fid.add_argument("account_fid", type=int, help="User's fid.")
    cmd_addr_by_fid.set_defaults(func=by_fid)

    cmd_addr_by_name = subparser.add_parser("byname", description="Get account info using name or fname")
    cmd_addr_by_name.add_argument("name", type=str, help="User's name.")
    cmd_addr_by_name.set_defaults(func=by_name)

    cmd_addr_from_secret = subparser.add_parser("fromsecret", description="Get account details using the secret seed phrase.")
    cmd_addr_from_secret.set_defaults(func=from_secret)

    args = parser.parse_args()

    CONF.update(get_conf(args=args))

    if 'func' in args:
        args.func(args)
    

if __name__ == '__main__':
    main()