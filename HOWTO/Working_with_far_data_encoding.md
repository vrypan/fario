# Working with the "far" data encoding.

Many of the `fario` tools output `Message` objects from stdin or read `Message` objects from stdin.
These are protobuffer-encoded binary objects that are not easy to manage using standard command-line
tools. To make these payloads command-line friendly, we serialize them and encode them using base64.

For example `fario-out --casts --lines=2 280` will output something like this:

```
$ fario-out --casts --limit=2 280

CoYCCAEQmAIYrr/aKiABKvcBGhkIwyASFMX9F/u1h2N8Cm8SkgG5/RbxFJkJItkBT24gdGhlIG90aGVyIGhhbmQgSSBoYXZlIGludmVzdGVkIGFsbCBteSBmcmVlIHRpbWUgZGV2ZWxvcGluZyBmb3IgdGhlIGh1YiBBUEksIHdoaWNoIGlzIHBhcnQgb2YgdGhlIHByb3RvY29sLiBGYXJjYXN0ZXIgaXMgYWxyZWFkeSBwZXJtaXNzaW9ubGVzcyBpbiBzbyBtYW55IHdheXMsIHdoeSBmb2N1cyBvbiBvbmUgb2YgdGhlIGZldyBmZWF0dXJlcyB0aGF0IGFyZSBub3Q/IDstKRIUqu3tM1go9wS0isYK/qMuWrnsxxcYASJAwDgGmkTZ3iKD72jxMKnDCCspdUDjDYQu+InQ2DswfkyStNg0R3gUJoiK0RigA5w/zyKC+R/pvWLkJlSe0xH0BigBMiBqI5tD+fXP7huCLOvu84aKOUlxZjDaMV1mlljQy5+fSA==
CpwCCAEQmAIYt73aKiABKo0CGhkIwyASFNKdz4C7T7lSgjgVUNJCyvZRIdVPIu8BSWYgdGhpcyB3YXMgc29tZXRoaW5nIG9mIGludGVyZXN0IHRvIG1lLCBhbmQgdHJ1c3RsZXNzIHdhcyBhbiBpbXBvcnRhbnQgZmFjdG9yIGluIG15IGRlY2lzaW9uLCBJIHdvdWxkbid0IGludmVzdCBteSB0aW1lIG9yIGVmZm9ydCBpbiBjaGFubmVscyAoYXQgYWxsKSByaWdodCBub3csIGJlY2F1c2UgSSB3b3VsZCBoYXZlIHRvIHRydXN0IHRoZSBXYXJwY2FzdCB0ZWFtIG9uIHdoYXQgdGhleSB3aWxsIGV2b2x2ZSB0by4SFPqKaX9y5Quy5V71XcojPwKB/W3wGAEiQE/sKXc7k1azyCoB1wWZ8v7IkukFNtstt0kVgcVLmtcUlJz2iGrp4nandFpQZ8TYBoAPuB2w2V3xysov6y77nQAoATIgaiObQ/n1z+4bgizr7vOGijlJcWYw2jFdZpZY0Mufn0g=
```

Each line of the above output is the result of `base64(serialize(message))`. You can use `fario2json` to convert these lines into json:

```
$ echo 'CoYCCAEQmAIYrr/aKiABKvcBGhkIwyASFMX9F/u1h2N8Cm8SkgG5/RbxFJkJItkBT24gdGhlIG90aGVyIGhhbmQgSSBoYXZlIGludmVzdGVkIGFsbCBteSBmcmVlIHRpbWUgZGV2ZWxvcGluZyBmb3IgdGhlIGh1YiBBUEksIHdoaWNoIGlzIHBhcnQgb2YgdGhlIHByb3RvY29sLiBGYXJjYXN0ZXIgaXMgYWxyZWFkeSBwZXJtaXNzaW9ubGVzcyBpbiBzbyBtYW55IHdheXMsIHdoeSBmb2N1cyBvbiBvbmUgb2YgdGhlIGZldyBmZWF0dXJlcyB0aGF0IGFyZSBub3Q/IDstKRIUqu3tM1go9wS0isYK/qMuWrnsxxcYASJAwDgGmkTZ3iKD72jxMKnDCCspdUDjDYQu+InQ2DswfkyStNg0R3gUJoiK0RigA5w/zyKC+R/pvWLkJlSe0xH0BigBMiBqI5tD+fXP7huCLOvu84aKOUlxZjDaMV1mlljQy5+fSA==' | fario2json

[
{
  "data": {
    "type": "MESSAGE_TYPE_CAST_ADD",
    "fid": "280",
    "timestamp": 89563054,
    "network": "FARCASTER_NETWORK_MAINNET",
    "castAddBody": {
      "parentCastId": {
        "fid": "4163",
        "hash": "xf0X+7WHY3wKbxKSAbn9FvEUmQk="
      },
      "text": "On the other hand I have invested all my free time developing for the hub API, which is part of the protocol. Farcaster is already permissionless in so many ways, why focus on one of the few features that are not? ;-)"
    }
  },
  "hash": "qu3tM1go9wS0isYK/qMuWrnsxxc=",
  "hashScheme": "HASH_SCHEME_BLAKE3",
  "signature": "wDgGmkTZ3iKD72jxMKnDCCspdUDjDYQu+InQ2DswfkyStNg0R3gUJoiK0RigA5w/zyKC+R/pvWLkJlSe0xH0Bg==",
  "signatureScheme": "SIGNATURE_SCHEME_ED25519",
  "signer": "aiObQ/n1z+4bgizr7vOGijlJcWYw2jFdZpZY0Mufn0g="
}
]
```

Converting these payloads to json allows users to use tools like `jq` to easily filter and manipulate them. (See [Examples](Examples.md)).

## Using fario-grep

However, some fields are raw bytes, and may be represented in various ways. For example, the `signer` field contains raw bytes that the
serializer converts to base64, but most apps will present as a hex number.

`fario-grep --signer` solves this problem. 

Let's see an example.

First, let's list all the signers I (fid=280) have approved:

```
fario-signers list --with-fnames 280

0x6a239b43f9f5cfee1b822cebeef3868a3949716630da315d669658d0cb9f9f48	1693349719	9152	@warpcast
0xd76ddc3123f7afedbcd4c8c8d66af0730c4429a401f605decfbd6e838bb6b098	1696122939	19150	@flink
0xa6f9575c9b0f9e7fcfb41b0a78370af75f26a15f7e98e6c5b087351f1acdfd65	1696710205	19150	@flink
0xf24c7e7c620e59ee6a9d8659a28e764c552fb87a59bbc91fb645e731611f3b6d	1697228651	19150	@flink
0x107499d25b2ab3fa2d0c1a769c859fae56ae50f1b65a25f448abffda4ef40f33	1697478699	20396	@fc1
0xd63ae1bf60ff8308721b3ce0dc4ab390d6fd7146dd869ba82fdc1b8de1ea1eea	1697479045	20396	@fc1
0xc421f513a8c302eae442da63aad0bf81d2907b7641a1bfcf97766553e2cc1e00	1697480529	20396	@fc1
0x532c81a2ea1d21bd17a4ba62adedc708ec0693b292398e6a8c8aec655f70bcea	1698746761	20108	@buidler
```

I want to find my recent likes that are signed by @buidler, ie. signer `0x532c81a2ea1d21bd17a4ba62adedc708ec0693b292398e6a8c8aec655f70bcea`.

I can export my recent likes using `fario-out --likes 280`, but if I decode them, I will get somethiong like this

```
$ fario-out --likes 280  | fario2json

[
{
  "data": {
    "type": "MESSAGE_TYPE_REACTION_ADD",
    "fid": "280",
    "timestamp": 89554687,
    "network": "FARCASTER_NETWORK_MAINNET",
    "reactionBody": {
      "type": "REACTION_TYPE_LIKE",
      "targetCastId": {
        "fid": "5620",
        "hash": "U/zNB+j/L9nF6omUa8VSusTd1m4="
      }
    }
  },
  "hash": "Fqbf3Ac6vpx3cwfPRXOh54y4H/8=",
  "hashScheme": "HASH_SCHEME_BLAKE3",
  "signature": "kVa5my2Yogz5Fk3QZ07Co3S85N+CoRzPAnHKF65jPcJ0SYcUJZpq3l1JLqJDvRhBsZ2RPhxWN1nG3Ck4FXkICQ==",
  "signatureScheme": "SIGNATURE_SCHEME_ED25519",
  "signer": "aiObQ/n1z+4bgizr7vOGijlJcWYw2jFdZpZY0Mufn0g="
},
... more messages ...

]
```

The signer is in base64, not hex...

One way to solve this is to convert the hex value to base 64 using `xxd` and `base64` and then filter using `jq`:

```
$ echo '532c81a2ea1d21bd17a4ba62adedc708ec0693b292398e6a8c8aec655f70bcea'| \
xxd -r -p | base64`

UyyBouodIb0XpLpire3HCOwGk7KSOY5qjIrsZV9wvOo=

$ fario-out --likes 280 | fario2json |\
jq '.[] | select(.signer=="UyyBouodIb0XpLpire3HCOwGk7KSOY5qjIrsZV9wvOo=")'

{
  "data": {
    "type": "MESSAGE_TYPE_REACTION_ADD",
    "fid": "280",
    "timestamp": 89372570,
    "network": "FARCASTER_NETWORK_MAINNET",
    "reactionBody": {
      "type": "REACTION_TYPE_LIKE",
      "targetCastId": {
        "fid": "19",
        "hash": "9SWDKnHANzDdzyvFBXDudVMZt3g="
      }
    }
  },
  "hash": "IjQ23JFfgrlF+zCU5np3kfuOcA4=",
  "hashScheme": "HASH_SCHEME_BLAKE3",
  "signature": "09cbAQsBo5/MvbMZ4K3MNmpjf6zHqvsAh1CspnJ2Njz2j1uTL5/BUZ0CfGTvXagKBJ16M95YfFr5wKISqU9ZDg==",
  "signatureScheme": "SIGNATURE_SCHEME_ED25519",
  "signer": "UyyBouodIb0XpLpire3HCOwGk7KSOY5qjIrsZV9wvOo="
}
... more messages ...
```

A much simpler way is to use `fario-grep`

```
$ fario-out --likes 280 | \
fario-grep --signer 0x532c81a2ea1d21bd17a4ba62adedc708ec0693b292398e6a8c8aec655f70bcea | \
fario2json

[
{
  "data": {
    "type": "MESSAGE_TYPE_REACTION_ADD",
    "fid": "280",
    "timestamp": 89372570,
    "network": "FARCASTER_NETWORK_MAINNET",
    "reactionBody": {
      "type": "REACTION_TYPE_LIKE",
      "targetCastId": {
        "fid": "19",
        "hash": "9SWDKnHANzDdzyvFBXDudVMZt3g="
      }
    }
  },
  "hash": "IjQ23JFfgrlF+zCU5np3kfuOcA4=",
  "hashScheme": "HASH_SCHEME_BLAKE3",
  "signature": "09cbAQsBo5/MvbMZ4K3MNmpjf6zHqvsAh1CspnJ2Njz2j1uTL5/BUZ0CfGTvXagKBJ16M95YfFr5wKISqU9ZDg==",
  "signatureScheme": "SIGNATURE_SCHEME_ED25519",
  "signer": "UyyBouodIb0XpLpire3HCOwGk7KSOY5qjIrsZV9wvOo="
},

... more records ...

]
```
