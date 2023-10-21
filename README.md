# fario

Farcaster command-line tools.

# Installation
First install [farcaster-py](https://github.com/vrypan/farcaster-py):

`pip install farcaster-py`

Then download this repo and add it to your `$PATH`:

`git clone https://github.com/vrypan/fario.git; export PATH="$PATH:$PWD/fario"`

(Any help packaging these scripts as a brew recipe, apt package, etc., will be appreciated!)

New commands: `fario-out`, `fario-in`, `fario-new-signer`, `fario-remove-signer`, `fario-sign`, `fario-cast`.

# fario-out

`fario-out` is used to export data from a farcaster hub.

```
usage: fario-out [-h] [--casts] [--links] [--recasts] [--likes] [--profile] [--all] [--limit LIMIT] [--hub HUB] [--wait WAIT] fid

Export Farcaster data.

positional arguments:
  fid            FID

options:
  -h, --help     show this help message and exit
  --casts        User casts
  --links        User links
  --recasts      User recasts
  --likes        User likes
  --profile      User profile data
  --all          Equivalent to --casts --links --recasts --likes --profile
  --limit LIMIT  Number of records. If more than one types of data are exported, the limit applies to each one separately.
  --hub HUB      Use the hub at <ADDRESS>. Ex. --hub 192.168.1.1:2283
  --wait WAIT    Wait for <WAIT> milliseconds between reads.
```

Example:

```
fario-out --casts --limit=3 280

CqUBCAEQmAIYhOWVKiABKpYBGhkIiDMSFFjk62TSNRH2rMWwEezWa3Xb33x2IktBZ3JlZSEgSGVyZSBpcyBvbmUgdGFrZSBvbiB0aGlzLiBodHRwczovL3dhcnBjYXN0LmNvbS92cnlwYW4uZXRoLzB4ODI3Njc0NzEyLAoqaHR0cHM6Ly93YXJwY2FzdC5jb20vdnJ5cGFuLmV0aC8weDgyNzY3NDcxEhTILBREMcmuwueQCDk9x61xVV1tMhgBIkCWEPcLABM+JJ8BM+BneFimHlbUpwfB0F6MqmQzKkMN++raovDlVrUzUcvoxggyHjBZV3UbXXMhKpjvwZ6jdf0JKAEyIGojm0P59c/uG4Is6+7zhoo5SXFmMNoxXWaWWNDLn59I
CpIDCAEQmAIYzNqVKiABKoMDEgEBIq8CQSBjb29sIGZlYXR1cmUgb2YgdGhlIEZhcmNhc3RlciBwcm90b2NvbCBpcyB0aGF0IHlvdSBjYW4gdXNlIGl0IG9mZi1saW5lISEhCgpXaGF0IEkgbWVhbjogWW91IGNhbiBjcmVhdGUgeW91ciBjYXN0cyBvZmYtbGluZSwgc3RvcmUgdGhlbSBpbiBhbiBhcHAsIGFuZCB3aGVuIHlvdSBhcmUgY29ubmVjdGVkLCBhbmQgdGhlIGFwcCBjYW4gc2VuZCB0aGVtIHRvIHRoZSBuZXR3b3JrICh3aXRoIGNvcnJlY3QgY3JlYXRpb24gdGltZXN0YW1wKS4gU2FtZSBmb3IgbGlrZXMsIHJlY2FzdHMsIGV0Yy4KCldoZW4gIGFpcnBsYW5lIG1vZGU/KgKgAjpIY2hhaW46Ly9laXAxNTU6Nzc3Nzc3Ny9lcmM3MjE6MHg0Zjg2MTEzZmMzZTk3ODNjZjNlYzlhNTUyY2JiNTY2NzE2YTU3NjI4EhSpd9GxFia8jwlXEaRJG27wsJlBNxgBIkA8jGq404X1287WN8p3Aswq+p/CuBEBzpnuHtLg6Oo7NWVuwLThb728I4t0fJTWoCh/OSPK1jr2bTrh7dI1Ft4DKAEyIGojm0P59c/uG4Is6+7zhoo5SXFmMNoxXWaWWNDLn59I
Cr8BCAEQmAIYr7mUKiABKrABGhgICBIUe0F3y5CCsYTflRJCWGEDmXqAk4QikwFJJ20gbW9yZSBpbnRlcmVzdGVkIGluIGRldiBzdHVmZi4gQVBJcywgbmV3IGNvbnRyYWN0cywgZXRjLiBUaGlua3MgSSBjb3VsZCB1c2UgdG8gYnVpbGQgb24gdG9wL3dpdGggWm9yYSBpbmZyYXN0cnVjdHVyZS4gUHJvZHVjdCBhbm5vdW5jZW1lbnRzIHRvby4SFKAZaHILx+EzYryjBDsSoGG2S3/eGAEiQEOQGEt1NjWdIQbISDElhoa5lvV/Pl2MYaVgfnTMrQl3NThLgxNHHG5xdY2x94VkgS7ApU7F4x4IcRLfK6N8jgUoATIgaiObQ/n1z+4bgizr7vOGijlJcWYw2jFdZpZY0Mufn0g=
```

The result is 3 lines of text. Each line is the corresponding farcaster message serialized and base64 encoded.

It is easy to decode a message using `fario2json`.

```
echo "CqUBCAEQmAIYhOWVKiABKpYBGhkIiDMSFFjk62TSNRH2rMWwEezWa3Xb33x2IktBZ3JlZSEgSGVyZSBpcyBvbmUgdGFrZSBvbiB0aGlzLiBodHRwczovL3dhcnBjYXN0LmNvbS92cnlwYW4uZXRoLzB4ODI3Njc0NzEyLAoqaHR0cHM6Ly93YXJwY2FzdC5jb20vdnJ5cGFuLmV0aC8weDgyNzY3NDcxEhTILBREMcmuwueQCDk9x61xVV1tMhgBIkCWEPcLABM+JJ8BM+BneFimHlbUpwfB0F6MqmQzKkMN++raovDlVrUzUcvoxggyHjBZV3UbXXMhKpjvwZ6jdf0JKAEyIGojm0P59c/uG4Is6+7zhoo5SXFmMNoxXWaWWNDLn59I" | ./fario2json | jq
[
  {
    "data": {
      "type": 1,
      "fid": 280,
      "timestamp": 88437380,
      "network": 1,
      "cast_add_body": {
        "parent_cast_id": {
          "fid": 6536,
          "hash": "0x58e4eb64d23511f6acc5b011ecd66b75dbdf7c76"
        },
        "text": "Agree! Here is one take on this. https://warpcast.com/vrypan.eth/0x82767471",
        "embeds": [
          {
            "url": "https://warpcast.com/vrypan.eth/0x82767471"
          }
        ]
      }
    },
    "hash": "0xc82c144431c9aec2e79008393dc7ad71555d6d32",
    "hash_scheme": 1,
    "signature": "0x9610f70b00133e249f0133e0677858a61e56d4a707c1d05e8caa64332a430dfbeadaa2f0e556b53351cbe8c608321e305957751b5d73212a98efc19ea375fd09",
    "signature_scheme": 1,
    "signer": "0x6a239b43f9f5cfee1b822cebeef3868a3949716630da315d669658d0cb9f9f48"
  }
]
```

Try: `fario-out --all --limit=5 2 | fario2json | jq`

# fario-in

`fario-in` is used to post data (messages) to a farcaster hub. Input is read from stdin and it is expected to be base64 encoded serialized protobuf messages, like the ones exported by `fario-out`.

```
usage: fario-in [-h] [--hub HUB] [--wait WAIT]

Send messages to Farcaster hub.

options:
  -h, --help   show this help message and exit
  --hub HUB    Use the hub at <ADDRESS>. Ex. --hub 192.168.1.1:2283
  --wait WAIT  Wait for <WAIT> milliseconds between message submissions.
```

# fario-new-signer

Create a new signer for an application and approve it using a user's private key.

```
usage: fario-new-signer [-h] [--provider PROVIDER] [--user_fid USER_FID] [--user_key USER_KEY] [--app_fid APP_FID] [--app_key APP_KEY]

Create a new signer

options:
  -h, --help           show this help message and exit
  --provider PROVIDER  OP Eth provider endpoint
  --user_fid USER_FID  User's fid.
  --user_key USER_KEY  User's private key in hex.
  --app_fid APP_FID    Application's fid.
  --app_key APP_KEY    Application's private key in hex.
```

# fario-remove-signer

Remove a signer already approved by a user.

```
usage: fario-remove-signer [-h] [--provider PROVIDER] [--user_key USER_KEY] signer

Remove signer

positional arguments:
  signer               Signer's public key in hex.

options:
  -h, --help           show this help message and exit
  --provider PROVIDER  OP Eth provider endpoint
  --user_key USER_KEY  User's private key in hex.
  ```

# fario-sign

It reads messages in `far` format from stdin, signs them using a new signer, and outputs them in `far` format to stdout.

```
usage: fario-sign [-h] key

Sign (or re-sign) messages uing a new signer.

positional arguments:
  key         Signer's private key

options:
  -h, --help  show this help message and exit
```

Example:
Compare the output (hashes, signers and signatures) of the following commands:

1. ```fario-out --casts --limit=5 280 | fario2json | jq```
2. ```fario-out --casts --limit=5 280 | fario-sign <key> | fario2json```

You could pipe the output of `fario-sign` to `fario-in` to post the new messages to a hub. 

Posting these messages to a hub can fail for various reasons:
1. Message hash is already posted. (i.e. you can repost the same message, even if the signature is changed)
2. Signer is not approved by the user: You can't post messages from an `fid` that has not approved the signer.
3. Message deleted: in many cases, deleting a cast leaves a "remove" message on the hubs, containing the removed messages hash. You can't post a new message with the same hash.

**VERY INTERESTING USE CASE**

However, you can use `fario-out` to backup your content, remove a signer (which results in all mesages signed by it to be removed!), then use `fario-sign` and `fario-in` to re-sign them with a new signer and upload them to farcaster!

# Other scripts

`fario-cast` is a simple script that can be used to cast plain text messages (no mentions, or embeds).
