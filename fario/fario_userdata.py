# SPDX-FileCopyrightText: 2024-present Panayotis Vryonis <vrypan@gmail.comm>
#
# SPDX-License-Identifier: MIT
import os
import click
import time
from dotenv import load_dotenv

from . __about__ import version
from . config import get_conf
from farcaster import Message, FARCASTER_EPOCH
from farcaster.HubService import HubService
from farcaster.fcproto.message_pb2 import SignatureScheme, HashScheme, UserDataType

USER_DATA_TYPES = {
    'none': UserDataType.USER_DATA_TYPE_NONE,
    'pfp': UserDataType.USER_DATA_TYPE_PFP,
    'display': UserDataType.USER_DATA_TYPE_DISPLAY,
    'bio': UserDataType.USER_DATA_TYPE_BIO,
    'url': UserDataType.USER_DATA_TYPE_URL,
    'username': UserDataType.USER_DATA_TYPE_USERNAME
}

@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=version, prog_name="fario-userdata")
def fario_user_data():
    """Farcaster Network Mapper
    """
    CONFIG_FILE = os.path.expanduser('~/.fario')
    load_dotenv(CONFIG_FILE)
    load_dotenv()
    

@fario_user_data.command()
@click.option('--hub', default='hoyt.farcaster.xyz:2283', help="Use the hub at <ADDRESS:PORT>. Ex. --hub 192.168.1.1:2283", envvar='hub')
@click.option('--ssl', is_flag=True, default=False, help="Use SSL")
@click.option('--signer', help="Signer's private key", required=True, envvar='signer')
@click.argument('user-fid', type=click.INT)
@click.argument('data-type', type=click.Choice([k for k in USER_DATA_TYPES.keys()], case_sensitive=False), required=True)
@click.argument('data-value')
def set(hub, ssl, signer, user_fid, data_type, data_value):

    timestamp = int(time.time())-FARCASTER_EPOCH
    hub = HubService(hub, use_async=False, use_ssl=ssl)

    message_builder = Message.MessageBuilder(
        HashScheme.HASH_SCHEME_BLAKE3, 
        SignatureScheme.SIGNATURE_SCHEME_ED25519, 
        bytes.fromhex(signer[2:])
    )
    
    data = message_builder.user_data.add(
        fid = user_fid, 
        data_type = USER_DATA_TYPES[data_type],
        data_value = data_value
    )

    msg  = message_builder.message(data)

    ret  = hub.SubmitMessage(msg)
    
    print(f"USER_DATA_TYPE_{data_type.upper()} set to {data_value}")


@fario_user_data.command()
@click.option('--hub', default='hoyt.farcaster.xyz:2283', help="Use the hub at <ADDRESS:PORT>. Ex. --hub 192.168.1.1:2283", envvar='hub')
@click.option('--ssl', is_flag=True, default=False, help="Use SSL")
@click.argument('user-fid', type=click.INT)
@click.argument('data-type', type=click.Choice([k for k in USER_DATA_TYPES.keys()], case_sensitive=False), required=True)
def get(hub, ssl, user_fid, data_type):
    hub = HubService(hub, use_async=False, use_ssl=ssl)
    response = hub.GetUserDataByFid(user_fid, 100)
    for c in response.messages:
        if c.data.user_data_body.type == USER_DATA_TYPES[data_type]:
            print(c.data.user_data_body.value)




