#!/usr/bin/env python
from farcaster.HubService import HubService
#from . config import get_conf
import os
import sys
import re
import argparse
from datetime import datetime
from dotenv import load_dotenv
import sqlite3
from termcolor import colored
import textwrap
from farcaster.fcproto.message_pb2 import Message, ReactionType
from farcaster import FARCASTER_EPOCH

def get_conf(required=[], args=None) -> str:

    CONFIG_FILE = os.path.expanduser('~/.fario')

    load_dotenv(CONFIG_FILE)
    load_dotenv()

    conf = {}
    params = ( 
        'hub', 'user_fid', 'user_key', 'app_fid', 'app_key', 'signer', 'op_eth_provider'
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

class Proxy:
    TTL = 60*5
    def __init__(self):
        self.conf = get_conf(required=['hub'])
        self.hub = HubService(self.conf['hub'], use_async=False)
        self.files_path = os.path.expanduser('~/.fcsh')
        if not os.path.isdir(self.files_path):
            os.mkdir(self.files_path)
        self.db_path = os.path.join(self.files_path, 'db')
        if not os.path.isfile(self.db_path):
            self.db_open()
            self.db_create()
        else:
            self.db_open()
        
    def db_open(self):
        self.db_conn = sqlite3.connect(self.db_path, isolation_level="IMMEDIATE")
        self.db_conn.row_factory = sqlite3.Row
        self.db_cur = self.db_conn.cursor()
        return self

    def db_close(self):
        self.db_conn.commit()
        self.db_conn.close()

    def db_create(self):
        self.db_cur.execute("""
            CREATE TABLE IF NOT EXISTS users(
                fid INTEGER,
                fname TEXT,
                name TEXT,
                upd_ts INTEGER,
                primary key(fid))
            """)
        self.db_cur.execute("CREATE UNIQUE INDEX fname_idx ON users(fname)")
        self.db_cur.execute("CREATE UNIQUE INDEX name_idx ON users(name)")

        self.db_cur.execute("""
            CREATE TABLE IF NOT EXISTS user_data(
                fid INTEGER,
                data_type INTEGER,
                value TEXT,
                upd_ts INTEGER,
                primary key(fid,data_type))
            """)

        self.db_cur.execute("""
            CREATE TABLE IF NOT EXISTS casts(
                fid INTEGER,
                hash TEXT,
                parent TEXT,
                msg BLOB,
                upd_ts INTEGER,
                primary key(fid,hash))
            """)
        self.db_cur.execute("CREATE INDEX cast_parent_idx ON casts(parent)")
        self.db_cur.execute("""
            CREATE TABLE IF NOT EXISTS reactions(
                fid INTEGER,
                hash TEXT,
                u_fid INTEGER,
                reaction_type INTEGER,
                ts INTEGER,
                upd_ts INTEGER,
                primary key(fid, hash, u_fid, reaction_type))
            """)
        self.db_cur.execute("CREATE INDEX reactions_ts_idx ON reactions(fid, hash, u_fid, reaction_type, ts)")
        self.db_conn.commit()

    def get_fid_by_name(self, name):
        ret  = self.hub.GetUsernameProof(name)
        if ret:
            return ret.fid
        else:
            print('Error: Name not found.', file=sys.stderr)
            sys.exit(1)

    def get_user_by_fid(self, fid):
        self.db_cur.execute("SELECT * FROM users WHERE fid=?", (fid,))
        r = self.db_cur.fetchone()
        if r:
            return r
        else:
            ret  = self.hub.GetUserNameProofsByFid(fid, page_size=None)
            proofs = [ m.name.decode('ascii') for m in ret.proofs ]
            fname = ''
            name = ''
            ts = int(datetime.now().timestamp())
            for n in proofs:
                if n[-4:] =='.eth':
                    name = n
                else:
                    fname = n
            self.db_cur.execute("INSERT OR REPLACE INTO users(fid, fname, name, upd_ts) VALUES(?,?,?,?)", (fid, fname, name, ts))
            self.db_conn.commit()
            return {'fid': fid, 'fname': fname, 'name': name }

    def get_username_by_fid(self, fid):
        user = self.get_user_by_fid(fid)
        if user['name']:
            return user['name']
        elif user['fname']:
            return user['fname']
        else:
            return str(fid)
    def hdb_get_user_data(self, fid, user_data_type):
        ts = int(datetime.now().timestamp())
        self.db_cur.execute("SELECT * FROM user_data WHERE fid=? AND data_type=? AND upd_ts>?", (fid,user_data_type,ts-(self.TTL*10)))
        r = self.db_cur.fetchone()
        if r:
            return(r['value'])
        else:
            msg = self.hub.GetUserData(fid, user_data_type)
            if not msg:
                value = None
            else:
                value = msg.data.user_data_body.value
            self.db_cur.execute(
                "INSERT OR REPLACE INTO user_data(fid,data_type,value,upd_ts) VALUES(?,?,?,?)",
                (fid, user_data_type, value, ts)
            )
            self.db_conn.commit()
            return value

    def pp_date(self, t: int) -> str:
        ret = '(' + datetime.fromtimestamp(t+FARCASTER_EPOCH).strftime('%Y-%m-%d %H:%M:%S') + ')'
        return colored( ret, 'light_grey')
    def pp_cast_id(self, fid:int, hash:str) -> str:
        out = colored(f"@{self.get_username_by_fid(fid)}", "magenta", attrs=["bold"])
        out += colored(f"/0x{hash} ", 'light_grey')
        return out
    def pp_link(self, l: str) -> str:
        return str(colored(l.strip(), "blue", attrs=['underline']))
    def pp_fid(self, fid: int) -> str:
        return colored(f"@{fid}", "magenta", attrs=["bold"])
    def pp_cast(self, m: Message, txt_offset=0 ) -> str:
        out = ""
        out +=  self.pp_cast_id(m.data.fid, m.hash.hex()) + self.pp_date(m.data.timestamp) + "\n"
        if m.data.cast_add_body.parent_cast_id.fid and not txt_offset:
            parent_fid = m.data.cast_add_body.parent_cast_id.fid
            parent_hash = m.data.cast_add_body.parent_cast_id.hash.hex()
            out = out + " "*txt_offset + f"↳ In reply to {self.pp_cast_id(parent_fid, parent_hash)}" + "\n"
        if m.data.cast_add_body.parent_url:
            out = out + " "*txt_offset + f"↳ In reply to {self.pp_link(m.data.cast_add_body.parent_url)}" + "\n"
        text = m.data.cast_add_body.text
        if hasattr(m.data.cast_add_body, 'mentions_positions'):
            offset = 0
            for i in range(len(m.data.cast_add_body.mentions)):
                pos = m.data.cast_add_body.mentions_positions[i]+offset
                username = f"{self.pp_fid(self.get_username_by_fid(m.data.cast_add_body.mentions[i]))}"
                text = text[0:pos] + username + text[pos:]
                offset += len(username)
        out += "\n".join([ "\n".join(textwrap.wrap(l, width=70)) for l in text.splitlines() ])
        if hasattr(m.data.cast_add_body, 'embeds'):
            for embed in m.data.cast_add_body.embeds:
                if hasattr(embed,'url'):
                    out += '\n> ' + self.pp_link(embed.url)
        lines = out.splitlines()
        if txt_offset:
            out2 = "  "*txt_offset + '┌ ' + lines[0]
        else:
            out2 = "  "*txt_offset + '┌ ' + lines[0]
        out2 += "\n"+"  "*txt_offset + '│ ' + ("\n"+"  "*txt_offset + '│ ').join(lines[1:])
        out2 += "\n" + "  "*txt_offset + '└─' 
        return out2

    def get_casts_by_fid(self, fid:int, count: int):
        ret = self.hub.GetCastsByFid(fid, count)
        messages = [m for m in ret.messages]
        messages.reverse()
        i=0
        for m in messages:
            i +=1
            print(self.pp_cast(m))
            if i > count:
                break
    def _get_cast_by_castid(self, fid:int, hash:str) -> Message:
        self.db_cur.execute("SELECT * FROM casts users WHERE fid=? AND hash=?", (fid,hash))
        cast = self.db_cur.fetchone()
        if cast:
            msg = Message()
            msg.ParseFromString(cast['msg'])
            return msg
        else:
            cast  = self.hub.GetCast(fid, hash)
            if not cast:
                return None
            self._db_put_cast(cast)
            return cast
    def _db_put_cast(self, cast: Message):
        ts = int(datetime.now().timestamp())
        if cast.data.cast_add_body.parent_cast_id.fid:
            parent_fid = cast.data.cast_add_body.parent_cast_id.fid
            parent_hash = '0x' + cast.data.cast_add_body.parent_cast_id.hash.hex()
            parent = f"{parent_fid}/{parent_hash}"
        elif cast.data.cast_add_body.parent_url:
            parent = cast.data.cast_add_body.parent_url
        else:
            parent = ''
        self.db_cur.execute("INSERT or REPLACE INTO casts(fid, hash, msg, parent, upd_ts) VALUES(?,?,?,?,?)", 
            (cast.data.fid, '0x'+cast.hash.hex(), cast.SerializeToString(), parent, ts)
        )
        self.db_conn.commit()

    def hdb_get_reactions_by_fid(self, fid:int, reaction_type: int):
        username = self.get_username_by_fid(fid)
        out = ''
        messages = self.hub.GetReactionsByFid(fid, reaction_type, 100)
        #print(messages)
        heart = colored("❤", "red", attrs=["bold"])
        recast = colored("♺", "green", attrs=["bold"])
        for r in messages.messages:
            #print(r.data.reaction_body.type)
            if r.data.reaction_body.type == 1: #like
                dt = datetime.fromtimestamp(r.data.timestamp+FARCASTER_EPOCH).strftime('%Y-%m-%d %H:%M:%S')
                if r.data.reaction_body.target_cast_id.fid: # CastId
                    cast_id = self.pp_cast_id(
                        r.data.reaction_body.target_cast_id.fid,
                        r.data.reaction_body.target_cast_id.hash.hex()
                        )
                    desc = f"liked {cast_id}"
                out = f'{dt} {heart} {desc} \n' + out
            if r.data.reaction_body.type == 2: #recast
                dt = datetime.fromtimestamp(r.data.timestamp+FARCASTER_EPOCH).strftime('%Y-%m-%d %H:%M:%S')
                if r.data.reaction_body.target_cast_id.fid: # CastId
                    cast_id = self.pp_cast_id(
                        r.data.reaction_body.target_cast_id.fid,
                        r.data.reaction_body.target_cast_id.hash.hex()
                        )
                    desc = f"recasted {cast_id}"
                out = f'{dt} {recast} {desc} \n' + out
        return out

    def hdb_get_reactions_by_cast(self, fid:int, oxhash:str, reaction_type: int):
        self.db_cur.execute("SELECT * FROM reactions WHERE fid=? AND hash=? AND reaction_type=? ORDER BY ts DESC", (fid, oxhash,1))
        r = self.db_cur.fetchone() 
        if r and (int(datetime.now().timestamp()) - int(r['ts']) < self.TTL):
            return self.db_cur.fetchall()
        else:            
            reactions = []
            page_token=1
            while page_token:
                if page_token==1:
                    page_token=None
                messages = self.hub.GetReactionsByCast(fid, oxhash, reaction_type, 100, page_token)
                page_token = messages.next_page_token
                for r in messages.messages:
                    u_fid = r.data.fid
                    ts = r.data.timestamp + FARCASTER_EPOCH
                    self.db_cur.execute(
                        "INSERT OR REPLACE INTo reactions(fid,hash, u_fid, reaction_type, ts) VALUES(?,?,?,?,?)", 
                        (fid, oxhash, u_fid, reaction_type, ts)
                    )
                    self.db_conn.commit()
            self.db_cur.execute(
                "SELECT * FROM reactions WHERE fid=? AND hash=? AND reaction_type=? ORDER BY ts DESC", 
                (fid, oxhash,1)
            )
            return self.db_cur.fetchall() 

    def h_get_cast_ancestors(self, fid:int, oxhash:str) -> {}:
        cast = self._get_cast_by_castid(fid, oxhash)
        parent_fid = cast.data.cast_add_body.parent_cast_id.fid
        while parent_fid:
            cast = self._get_cast_by_castid(parent_fid, '0x' + cast.data.cast_add_body.parent_cast_id.hash.hex() )
            parent_fid = cast.data.cast_add_body.parent_cast_id.fid
        return {"fid":cast.data.fid, "hash":'0x'+cast.hash.hex()}

    def h_get_cast_children(self, fid:int, oxhash:str):
        cast = self._get_cast_by_castid(fid, oxhash)
        children = self.hub.GetCastsByParentCast(fid, oxhash)
        c_list = [c for c in children.messages]
        for c in c_list:
            self._db_put_cast(c)
            self.h_get_cast_children( c.data.fid, '0x'+c.hash.hex() )

    def db_pp_cast_tree(self, fid:int, oxhash:str):
        top_cast = self.h_get_cast_ancestors(fid, oxhash)
        self.h_get_cast_children(top_cast['fid'], top_cast['hash'])
        return self.db_pp_cast_children(top_cast['fid'], top_cast['hash'])

    def db_pp_cast_children(self, fid:int, oxhash:str, offset=0, out=''):
        cast = self._get_cast_by_castid(fid, oxhash)
        out = ''
        children = self.db_cur.execute("SELECT * FROM casts WHERE parent=?", ( (f"{fid}/{oxhash}",) ))
        if children:
            rows = [row for row in children]
            for row in rows:
                c = Message()
                c.ParseFromString(row['msg'])
                out = out + self.db_pp_cast_children(c.data.fid, '0x'+c.hash.hex(), offset+1, out)
        out = self.pp_cast(cast, offset) + "\n" + out
        return out

    def db_pp_cast_children_orig(self, fid:int, oxhash:str, offset=0, out=''):
        cast = self._get_cast_by_castid(fid, oxhash)
        print(self.pp_cast(cast, offset))
        children = self.db_cur.execute("SELECT * FROM casts WHERE parent=?", ( (f"{fid}/{oxhash}",) ))
        if children:
            rows = [row for row in children]
            for row in rows:
                c = Message()
                c.ParseFromString(row['msg'])
                self.db_pp_cast_children(c.data.fid, '0x'+c.hash.hex(), offset+1, out)

    def get_cast(self, fid:int, hash: str, expand=False, append='', offset=0):
        ret = self._get_cast_by_castid(fid, hash)
        cast_txt = "\n" + self.pp_cast(ret, offset) + append
        if expand and ret.data.cast_add_body.parent_cast_id.fid:        
            cast_txt = self.get_cast(
                ret.data.cast_add_body.parent_cast_id.fid, '0x'+ret.data.cast_add_body.parent_cast_id.hash.hex(), True, cast_txt, offset
                )
        else:
            print(cast_txt)

def main():
    parser = argparse.ArgumentParser(prog="termcast", description="Terminal-based farcaster client")
    #parser.add_argument("--expand", help="Expand cast threads", action="store_true")
    parser.add_argument("--expand", type=int, default=0, help="Expand thread, level=<EXPAND>")
    parser.add_argument("uri", type=str)
    args = parser.parse_args()
    
    p = Proxy()

    uri = re.findall('^@(\w*)(\.eth)?(/\w*)?(/\w*)?$', args.uri)
    if not uri:
        sys.exit(1)

    username = uri[0][0] + uri[0][1]
    path = uri[0][2]
    path2 = uri[0][3]

    # Look up fid if needed
    if not re.match("^\d*$", username):
        fid = p.get_fid_by_name(username)
    else:
        fid = int(username)

    USER_DATA_TYPE={
        'pfp':1,
        'display':2,
        'bio':3,
        'url':5,
        'username':6
    }
    if path[1:] in USER_DATA_TYPE:
        out = p.hdb_get_user_data(fid,USER_DATA_TYPE[path[1:]])
        print(out)
        sys.exit(0)
        # farcaster://<user>/(pfp|bio|url|username|casts|<link_type>)?
    if path[1:] == 'likes':
        out = p.hdb_get_reactions_by_fid(fid=fid, reaction_type=None)
        print(out)
    if path == "/casts": 
        # List all casts
        p.get_casts_by_fid(fid, 20)
        sys.exit(0)
    elif path[0:3] == '/0x':
        if path2 not in ('/likes', '/recasts'):
            # Show cast
            if args.expand<2:
                p.get_cast(fid, path[1:], args.expand)
                print()
            else:
                print( p.db_pp_cast_tree(fid, path[1:]) )
                print()
                #from pick import pick
                #options = p.db_pp_cast_tree(fid, path[1:]).splitlines()
                #option, index = pick(options)
                #print(option)
                #print(index)
        elif path2 == '/likes':
            ret = p.hdb_get_reactions_by_cast(fid, path[1:], 1)
            for r in ret:
                username = p.get_username_by_fid(r['u_fid'])
                print(p.pp_fid(username))

if __name__ == '__main__':
    main()