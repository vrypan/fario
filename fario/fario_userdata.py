#!/usr/bin/env python
import sys
import time
from farcaster.HubService import HubService
from farcaster.fcproto.message_pb2 import SignatureScheme, HashScheme, UserDataType
from farcaster import Message, FARCASTER_EPOCH
import argparse
from . config import get_conf
from . __about__ import version


"""
USER_DATA_TYPE_NONE = 0;
USER_DATA_TYPE_PFP = 1; // Profile Picture for the user
USER_DATA_TYPE_DISPLAY = 2; // Display Name for the user
USER_DATA_TYPE_BIO = 3; // Bio for the user
USER_DATA_TYPE_URL = 5; // URL of the user
USER_DATA_TYPE_USERNAME = 6; /
"""

USER_DATA_TYPES = {
    'none': UserDataType.USER_DATA_TYPE_NONE,
    'pfp': UserDataType.USER_DATA_TYPE_PFP,
    'display': UserDataType.USER_DATA_TYPE_DISPLAY,
    'bio': UserDataType.USER_DATA_TYPE_BIO,
    'url': UserDataType.USER_DATA_TYPE_URL,
    'username': UserDataType.USER_DATA_TYPE_USERNAME
}

def main():
    parser = argparse.ArgumentParser(prog="fario-userdata", description="Get/Set userdata")
    parser.add_argument('--version', action='version', version='%(prog)s v'+version)
    parser.add_argument("--hub", help="Use the hub at <ADDRESS>. Ex. --hub 192.168.1.1:2283", type=str)
    parser.add_argument("--ssl", help="Use SSL", action="store_true")
    parser.add_argument("--signer", type=str, help="Signer's private key")
    parser.add_argument("--user-fid", type=int, help="User's fid")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("key", type=str, help="Data type")
    parser.add_argument("value", type=str, help="Value")
    args = parser.parse_args()
    
    conf=get_conf(required=['hub', 'user_fid', 'signer'], args=args)
    user_fid = conf['user_fid']

    timestamp = int(time.time())-FARCASTER_EPOCH
    
    hub = HubService(conf['hub'], use_async=False, use_ssl=conf['ssl'])

    message_builder = Message.MessageBuilder(
        HashScheme.HASH_SCHEME_BLAKE3, 
        SignatureScheme.SIGNATURE_SCHEME_ED25519, 
        bytes.fromhex(conf['signer'][2:])
    )
    
    data = message_builder.user_data.add(
        fid = int(user_fid), 
        data_type = USER_DATA_TYPES[args.key],
        data_value = args.value
    )

    msg  = message_builder.message(data)

    ret  = hub.SubmitMessage(msg)
    if args.verbose:
        print(f"{USER_DATA_TYPES[key]} set to {value}")

if __name__ == '__main__':
    main()
