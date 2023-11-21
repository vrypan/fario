#!/usr/bin/env python

import os
import sys
import datetime
import base64
from farcaster.Signer import Signer, removeSigner
from nacl.signing import SigningKey
from blake3 import blake3
from farcaster.fcproto.message_pb2 import HashScheme, Message, MessageData
from . config import get_conf

import argparse
from . __about__ import version

def signer_add(args):
    conf = get_conf(
        required = ['op_eth_provider', 'user_fid', 'user_key', 'app_fid', 'app_key'],
        args = args
        )
    s = Signer( conf['op_eth_provider'], int(conf['user_fid']), conf['user_key'], int(conf['app_fid']), conf['app_key'] )

    tx_hash = s.approve_signer()
    signer_private_key = s.key
    signer_public_key = s.signer_pub()

    if not args.raw:
        print(f"=== New Signer approved =====================")
        print(f"Tx: {tx_hash}")
        print(f"User Fid: {conf['user_fid']}")
        print(f"App Fid: {conf['app_fid']}")
        print(f"Signer public key: 0x{s.signer_pub().hex()}")
        print(f"Signer private key: {s.key.hex()}")
        print(f"=== MAKE SURE YOU SAVE THE PRIVATE KEY!!! ===")
    else:
        print(f"{tx_hash}\t{conf['user_fid']}\t{conf['app_fid']}\t0x{s.signer_pub().hex()}\t{s.key.hex()}" )

def signer_revoke(args):
    conf = get_conf(
        required = ['op_eth_provider', 'user_key'],
        args = args
        )

    provider = conf['op_eth_provider']
    user_key = conf['user_key']

    tx = removeSigner(provider, user_key, args.signer)
    if not args.raw:
        print(f"Signer {args.signer} removed. Tx={tx}")
    else:
        print(tx)

def signer_list(args):
    conf = get_conf(
        required = ['hub'],
        args = args
        )
    hub_address = conf['hub']

    from farcaster.HubService import HubService
    hub = HubService(hub_address, use_async=False, use_ssl=conf['ssl'])
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
    conf = get_conf(
        required = ['signer'],
        args = args
    )

    signer=SigningKey(bytes.fromhex(conf['signer'][2:]))
    signer_pub_key=signer.verify_key.encode()

    for line in sys.stdin:
        m = Message.FromString(base64.b64decode(line))
        if m.hash_scheme == HashScheme.HASH_SCHEME_BLAKE3:
            data_serialized = m.data.SerializeToString()
            msg_hash = blake3(data_serialized).digest(length=20)
            msg_signature = signer.sign(msg_hash).signature
            m.signer=signer_pub_key
            m.signature=msg_signature
            if msg_hash != m.hash:
                if args.keep_hash == True:
                    print("Error: [fario-signers] New message hash != old message hash, but --keep-hash=True.",
                        file=sys.stderr)
                    sys.exit(1)
                else:
                    m.hash = msg_hash
                    m.data_bytes = data_serialized
            out = base64.b64encode(m.SerializeToString()).decode('ascii')
            print(out)
        else:
            print("Error: [fario-signers] HashScheme={m.hash_scheme} not supported.", file=sys.stderr)
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
    cmd_signer_add.add_argument("--user-fid", help="User's fid.")
    cmd_signer_add.add_argument("--user-key", help="User's private key in hex.")
    cmd_signer_add.add_argument("--app-fid", help="Application's fid.")
    cmd_signer_add.add_argument("--app-key", help="Application's private key in hex.")
    cmd_signer_add.set_defaults(func=signer_add)

    cmd_signer_remove = subparser.add_parser("remove", description="""Remove a signer.
        Using --raw will output only the tx_hash.""")
    cmd_signer_remove.add_argument("--op_eth_provider", help="OP Eth provider endpoint")
    cmd_signer_remove.add_argument("--user-key", help="User's private key in hex.")
    cmd_signer_remove.add_argument("signer", help="Signer's public key in hex.")
    cmd_signer_remove.set_defaults(func=signer_revoke)

    cmd_signer_list = subparser.add_parser("list", description="list signers")
    cmd_signer_list.add_argument("--hub", help="Use the hub at <HUB>. Ex. --hub 192.168.1.1:2283", type=str)
    cmd_signer_list.add_argument("--ssl", help="Use SSL", action="store_true")
    cmd_signer_list.add_argument('--with-fnames', action='store_true', help="Display the fname of the Signer owner.")
    cmd_signer_list.add_argument("fid", type=int, help="Signers for <FID>")
    cmd_signer_list.set_defaults(func=signer_list)

    cmd_signer_sign = subparser.add_parser("sign", 
        description="Read messages and sign (or re-sign) using a new signer.\n"
        "Reads from stdin, writes to stdout. In and out are in fario format.")
    cmd_signer_sign.add_argument("--signer", type=str, help="Signer's private key")
    cmd_signer_sign.add_argument('--keep-hash', default="false", action='store_true', help="Do not change the message hash.")
    cmd_signer_sign.set_defaults(func=signer_sign)    

    args = parser.parse_args()

    if 'func' in args:
        args.func(args)
    

if __name__ == '__main__':
    main()
