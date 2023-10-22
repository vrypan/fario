#!/usr/bin/env python
import os
import sys
import base64
from blake3 import blake3
from nacl.signing import SigningKey
from farcaster.fcproto.message_pb2 import HashScheme, Message, MessageData
from protobuf_to_dict import protobuf_to_dict

import argparse

def main():
    parser = argparse.ArgumentParser(prog="fario-sign", description="Sign (or re-sign) messages uing a new signer.")
    parser.add_argument("key", type=str, help="Signer's private key")
    args = parser.parse_args()

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
            m.data_bytes = data_serialized
            out = base64.b64encode(m.SerializeToString()).decode('ascii')
            print(out)
        else:
            print("HashScheme={m.hash_scheme} not supported.")
            sys.exit(1)

if __name__ == '__main__':
    main()