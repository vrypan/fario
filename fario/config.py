import os
import sys
from dotenv import load_dotenv
import argparse
from . __about__ import version

def get_conf(required=[], args=None) -> str:

    CONFIG_FILE = os.path.expanduser('~/.fario')

    load_dotenv(CONFIG_FILE)
    load_dotenv()

    conf = {}
    params = ( 
        'hub', 'user_fid', 'user_key', 'app_fid', 'app_key', 'signer', 'op_eth_provider', 'ssl'
    )
    for p in params:
        conf[p] = os.getenv(p,'')
        if args and hasattr(args, p) and getattr(args, p):
            conf[p] = getattr(args,p)
    if len(required)>0 :
        check_conf(conf, required)
    return conf
def check_conf(conf, keys):
    for k in keys:
        if not conf[k]:
            print(f"Error: {k} is not set. Use the corresponding option, "
                    "an environment varaible, or set it in ~/.fario", 
                file=sys.stderr)
            sys.exit(1)
            
def cmd_conf_get(args):
    conf = get_conf()
    print("Configuration (using ~/.fario, .env and environment variables).")
    for k in conf:
        print(f"{k:<15} {conf[k]}")

def cmd_conf_make(args):
    conf = get_conf()
    print("# Set variables according to your configuration and save to ~/.fario.")
    print("# You can also leave them blank and set them using each command's options.")
    for k in conf:
        print(f"{k}={conf[k]}")

def cmd_conf():
    parser = argparse.ArgumentParser(prog='fario-config')
    parser.add_argument('--version', action='version', version='%(prog)s v'+version)
    subparser = parser.add_subparsers()

    cmd_config_get = subparser.add_parser("get", 
        description="Print current configuration. Priority, high-to-low: environment, .env, ~/.fario"
    )
    cmd_config_get.set_defaults(func=cmd_conf_get)

    cmd_config_make = subparser.add_parser("make", 
        description="Read configuration and output (stdout) a sample config file."
    )
    cmd_config_make.set_defaults(func=cmd_conf_make)

    args = parser.parse_args()

    if 'func' in args:
        args.func(args)

if __name__ == '__main__':
    conf = get_conf()
    for k in conf:
        print(f"{k:<15}: {conf[k]}")