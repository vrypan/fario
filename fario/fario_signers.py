#!/usr/bin/env python

import os
import sys
import datetime
import base64
from dotenv import load_dotenv
from farcaster.Signer import Signer, removeSigner
from nacl.signing import SigningKey
from blake3 import blake3
from farcaster.fcproto.message_pb2 import HashScheme, Message, MessageData

import argparse
from . __about__ import version

def signer_add(args):
    load_dotenv()
    provider = args.provider if args.provider else os.getenv("OP_ETH_PROVIDER")
    user_fid = args.user_fid if args.user_fid else os.getenv("USER_FID")
    user_key = args.user_key if args.user_key else os.getenv("USER_PRIVATE_KEY")
    app_fid = args.app_fid if args.app_fid else os.getenv("APP_FID")
    app_key = args.app_key if args.app_key else os.getenv("APP_PRIVATE_KEY")

    if not (provider and user_fid and user_key and app_fid and app_key):
        if not args.raw:
            print('Missing parameters. Either define them in .env or as an option.')
        sys.exit(1)

    s = Signer( provider, int(user_fid), user_key, int(app_fid), app_key )

    tx_hash = s.approve_signer()
    signer_private_key = s.key
    signer_public_key = s.signer_pub()

    if not args.raw:
        print(f"=== New Signer approved =====================")
        print(f"Tx: {tx_hash}")
        print(f"User Fid: {user_fid}")
        print(f"App Fid: {app_fid}")
        print(f"Signer public key: 0x{s.signer_pub().hex()}")
        print(f"Signer private key: {s.key.hex()}")
        print(f"=== MAKE SURE YOU SAVE THE PRIVATE KEY!!! ===")
    else:
        print(f"{tx_hash}\t{user_fid}\t{app_fid}\t0x{s.signer_pub().hex()}\t{s.key.hex()}" )

def signer_revoke(args):
    load_dotenv()

    provider = args.provider if args.provider else os.getenv("OP_ETH_PROVIDER")
    user_key = args.user_key if args.user_key else os.getenv("USER_PRIVATE_KEY")

    if not (provider and user_key and args.signer):
        if not args.raw:
            print('Missing parameters. Either define them in .env or as an option.')
        sys.exit(1)
        
    tx = removeSigner(provider, user_key, args.signer)
    if not args.raw:
        print(f"Signer {args.signer} removed. Tx={tx}")
    else:
        print(tx)

def signer_list(args):
    load_dotenv()
    hub_address = args.hub if args.hub else os.getenv("FARCASTER_HUB")

    if not hub_address:
        print("No hub address. Use --hub of set FARCASTER_HUB in .env.")
        sys.exit(1)
    from farcaster.HubService import HubService
    hub = HubService(hub_address, use_async=False)
    r = hub.GetOnChainSignersByFid(args.fid)
    signers = []
    fid_to_name = {}
    for evt in r.events:
        signers.append({
            "pub_key": f"0x{evt.signer_event_body.key.hex()}",
            "timestamp": evt.block_timestamp,
            "signer_fid": int(evt.signer_event_body.metadata.hex()[64:128], 16)
            })
    for s in sorted(signers, key=lambda d: d['timestamp']):
        if args.with_fnames:
            if s['signer_fid'] not in fid_to_name:
                ret = hub.GetUserNameProofsByFid(s['signer_fid'])
                name = [ proof.name for proof in ret.proofs if proof.type==1][0].decode('ascii')
                fid_to_name[s['signer_fid']] = name
            print(f"{s['pub_key']}\t{s['timestamp']}\t{s['signer_fid']}\t@{fid_to_name[s['signer_fid']]}")
        else:
            print(f"{s['pub_key']}\t{s['timestamp']}\t{s['signer_fid']}")

def signer_sign(args):
    signer=SigningKey(bytes.fromhex(args.key[2:]))
    signer_pub_key=signer.verify_key.encode()

    for line in sys.stdin:
        m = Message.FromString(base64.b64decode(line))
        if m.hash_scheme == HashScheme.HASH_SCHEME_BLAKE3:
            data_serialized = m.data.SerializeToString()
            msg_hash = blake3(data_serialized).digest(length=20)
            msg_signature = signer.sign(msg_hash).signature
            m.signer=signer_pub_key
            m.signature=msg_signature
            m.hash = msg_hash
            m.data_bytes = data_serialized
            out = base64.b64encode(m.SerializeToString()).decode('ascii')
            print(out)
        else:
            print("HashScheme={m.hash_scheme} not supported.")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(prog='fario-signers')
    parser.add_argument('--version', action='version', version='%(prog)s v'+version)
    parser.add_argument('--raw', action='store_true', help="Output raw values, tab separated.")
    subparser = parser.add_subparsers()

    cmd_signer_add = subparser.add_parser("add", description="""Create a new signer.
        Using --raw will output tx_hash, user_fis, app_fid, signer_bublic_key,
        signer_private_key as a tab-separated list.
        """)
    cmd_signer_add.add_argument("--provider", help="OP Eth provider endpoint")
    cmd_signer_add.add_argument("--user_fid", help="User's fid.")
    cmd_signer_add.add_argument("--user_key", help="User's private key in hex.")
    cmd_signer_add.add_argument("--app_fid", help="Application's fid.")
    cmd_signer_add.add_argument("--app_key", help="Application's private key in hex.")
    cmd_signer_add.set_defaults(func=signer_add)

    cmd_signer_remove = subparser.add_parser("remove", description="""Remove a signer.
        Using --raw will output only the tx_hash.""")
    cmd_signer_remove.add_argument("--provider", help="OP Eth provider endpoint")
    cmd_signer_remove.add_argument("--user_key", help="User's private key in hex.")
    cmd_signer_remove.add_argument("signer", help="Signer's public key in hex.")
    cmd_signer_remove.set_defaults(func=signer_revoke)

    cmd_signer_list = subparser.add_parser("list", description="list signers")
    cmd_signer_list.add_argument("--hub", help="Use the hub at <HUB>. Ex. --hub 192.168.1.1:2283", type=str)
    cmd_signer_list.add_argument('--with_fnames', action='store_true', help="Display the fname of the Signer owner.")
    cmd_signer_list.add_argument("fid", type=int, help="Signers for <FID>")
    cmd_signer_list.set_defaults(func=signer_list)

    cmd_signer_sign = subparser.add_parser("sign", description="Sign (or re-sign) messages uing a new signer.")
    cmd_signer_sign.add_argument("key", type=str, help="Signer's private key")
    cmd_signer_sign.set_defaults(func=signer_sign)    

    args = parser.parse_args()

    if 'func' in args:
        args.func(args)
    

if __name__ == '__main__':
    main()
