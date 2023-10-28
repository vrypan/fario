# Create and use Signers with fario


## Before we start

Before we start let's see the parties involved:

1. The *user*. This is a farcaster account identified by `user_fid` and
a private key `user_key`. The private key is defined by the fid's custody address. If you
created your Farcaster account using Warpcast, the custody address and
the corresponding private key can be extracted from your "secret phrase",
often also called "seed phrase" or "mnemonic".

2. The *app*. This is the application (or any other Farcaster account),
identified by `app_fid` and the corresponding private key `app_key` (just like the user account).

You can either set these values in `~/.fario` (will work with homebrew installations), 
in `.env` or pass them as parameters to the commands we will use later. To make this guide more
eligible, I will assume that you have set these values in `~/.fario`.

It is easy to generate a `.fario` template by running `fario-config make`.

You will also need to [configure a hub](How_to_get_access_to_a_hub.md) and an
Ethereum provider such as alchemy or infura.

```
# your ~/.fario file will look like this

hub="IP:PORT"
user_fid=280 # this is my own account, @vrypan.eth
user_key="<set user's private key here>"
app_fid=20396 # this is @fc1, my test app.
app_key="<set app's private key here>"
op_eth_provider="https://opt-mainnet.g.alchemy.com/v2/........"

# since we will be creating a new signer, leave this blank to make the
# exxamples more clear.
signer="" 

```

## Create a Signer

**Important!!!** Before you proceed, you need to make sure that the custody wallet of `user_fid` has some OP ETH.
Signer approvals and removals require an onchain transaction, i.e. some gas. (Check the transactions bellow to see how much gas you will probably need.)

 ```
$ fario-signers add

=== New Signer approved =====================
Tx: 0xf138402c0073c7db8fe7ef07b3cb027063dd370dd18b3d060b7b932019d5efe6
User Fid: 280
App Fid: 20396
Signer public key: 0xa843398d1a212666e3077e314ddb99231c8466015d80d50747ada9cafa910af3
Signer private key: 0x95213475894383c3306811f27ccfd31cd2546c20cf738ab5d667f15fdd3e527d
=== MAKE SURE YOU SAVE THE PRIVATE KEY!!! ===
```

And [here is the transaction](https://optimistic.etherscan.io/tx/0xf138402c0073c7db8fe7ef07b3cb027063dd370dd18b3d060b7b932019d5efe6).

To make the following commands more generic, let's set some shell variables.

```
SIGNER_PUB=0xa843398d1a212666e3077e314ddb99231c8466015d80d50747ada9cafa910af3
SIGNER_KEY=0x95213475894383c3306811f27ccfd31cd2546c20cf738ab5d667f15fdd3e527d
```

Let's verify that the signer was actually approved.

```
$ fario-signers list 280 --with_fnames                                                                                                                                                                                  git:main*
0x6a239b43f9f5cfee1b822cebeef3868a3949716630da315d669658d0cb9f9f48	1693349719	9152	@warpcast
0xd76ddc3123f7afedbcd4c8c8d66af0730c4429a401f605decfbd6e838bb6b098	1696122939	19150	@flink
0xa6f9575c9b0f9e7fcfb41b0a78370af75f26a15f7e98e6c5b087351f1acdfd65	1696710205	19150	@flink
0xf24c7e7c620e59ee6a9d8659a28e764c552fb87a59bbc91fb645e731611f3b6d	1697228651	19150	@flink
0x107499d25b2ab3fa2d0c1a769c859fae56ae50f1b65a25f448abffda4ef40f33	1697478699	20396	@fc1
0xd63ae1bf60ff8308721b3ce0dc4ab390d6fd7146dd869ba82fdc1b8de1ea1eea	1697479045	20396	@fc1
0xc421f513a8c302eae442da63aad0bf81d2907b7641a1bfcf97766553e2cc1e00	1697480529	20396	@fc1
0x025b94fccad75c41da422915fdb6e39834bbc157fb951d9f62894d18ec6f1424	1697483087	20396	@fc1
0x6538d196fa3aa0e3f7940c6b5b5ab0a04e9b2cf784f76047ecf3e00645556d95	1697578435	20396	@fc1
0xfceb40d416ddee5c43a43507420a10d62820d1c1aa0953251d9a35989c51423a	1697578903	20396	@fc1
0xabf4ae24d9a8a4471fdaadd7adc7bd78e171b321fc80a979e377464bef9af3cc	1697784333	20396	@fc1
0xe92fb9e116315aa6c823b8555ea8a0750a65174af793eef0f77319b00cfd3f4b	1697788797	20396	@fc1
0x3af178d1995de3a9fd5f59e04d21a3955c32cfced2c0bbe07b8d516c5255786a	1697794601	20396	@fc1
0x77153bc8bb5f62e3295f88ef6e73a3252d39159d2c7858f6aad524acb0761646	1697794679	20396	@fc1
0xa843398d1a212666e3077e314ddb99231c8466015d80d50747ada9cafa910af3	1698166655	20396	@fc1
```

OK: The last line contains our Signer public key.

## Cast with the newly created Signer

Now, **ANYONE** who holds the Signer private key can cast on behalf of my account, @vrypan.eth.

`fario-cast --key=$SIGNER_KEY --user-fid=280 "Hello world"`

I waited a few seconds, and refreshed my profile:

![screenshot](hello_world_1.png)

## Remove the Signer

Now let's remove the signer. I don't want someone (you!) who reads this guide to be able to post
on my account, or delete my casts:

```
$ fario-signers remove $SIGNER_PUB

Signer 0xa843398d1a212666e3077e314ddb99231c8466015d80d50747ada9cafa910af3 removed. 
Tx=0xb48a5ad945806052fe025121179369d72c53b29b48557dd2efc76d294ff9133d
```

You can see the transaction [here](https://optimistic.etherscan.io/tx/0xb48a5ad945806052fe025121179369d72c53b29b48557dd2efc76d294ff9133d).

Let's try to use the Signer again.

```
fario-cast --key=$SIGNER_KEY --user-fid=280 "Hello world" 

Traceback (most recent call last):
  File "/Users/vrypan/Devel/far/venv/bin/fario-cast", line 8, in <module>
    ... more debug info ...
	details = "invalid signer: signer 0xa843398d1a212666e3077e314ddb99231c8466015d80d50747ada9cafa910af3 not found for fid 280"
	debug_error_string = "UNKNOWN:Error received from peer  {grpc_message:"invalid signer: signer 0xa843398d1a212666e3077e314ddb99231c8466015d80d50747ada9cafa910af3 not found for fid 280", grpc_status:3, created_time:"2023-10-24T20:09:43.534375+03:00"}"
```

### Important!!! Now that the signer was removed, my cast is also removed!!!

Any casts, likes, or follows you do using a Signer, they are removed once the signer is removed.

However, if the Signer deletes your casts, they are gone. They will not show up if you remove
the Signer.