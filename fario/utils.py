import os
import sys
from dotenv import load_dotenv

def get_conf(args=None) -> str:

    CONFIG_FILE = os.path.expanduser('~/.fario')

    load_dotenv(CONFIG_FILE)
    load_dotenv()
    
    hub_address = os.getenv("FARCASTER_HUB")
    if args and hasattr(args, 'hub') and args.hub:
        hub_address = args.hub

    user_fid = os.getenv("USER_FID")
    if args and hasattr(args, 'user_fid') and args.user_fid:
        user_fid = args.user_fid

    user_key = os.getenv("USER_PRIVATE_KEY")
    if args and hasattr(args, 'user_key') and args.user_key:
        user_key= args.user_key

    app_fid = os.getenv("APP_FID")
    if args and hasattr(args, 'app_fid') and args.app_fid:
        app_fid= args.app_fid

    app_key = os.getenv("APP_PRIVATE_KEY")
    if args and hasattr(args, 'app_key') and args.app_key:
        app_key = args.app_key

    signer = os.getenv("APP_SIGNER_KEY")
    if args and hasattr(args, 'signer') and args.signer:
        signer = args.signer

    return {
        'hub_address': hub_address,
        'user_fid': user_fid,
        'user_key': user_key,
        'app_fid': app_fid,
        'app_key': app_key,
        'signer': signer
    }

if __name__ == '__main__':
    conf = get_conf()
    for k in conf:
        print(f"{k:<15}: {conf[k]}")