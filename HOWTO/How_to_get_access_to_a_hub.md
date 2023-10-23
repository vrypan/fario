# Hubs: Getting access to a Hub.

Date: 2023-10-23

In order to use `fario` you will need access to a Farcaster hub. At the time this
is written, Farcaster hubs have relatively low requirements. According to
[Hubble documantation](https://www.thehubble.xyz/intro/install.html) you need:

- 8 GB of RAM
- 2 CPU cores or vCPUs
- 20 GB of free storage
- A public IP address with ports 2282 - 2285 exposed

I would also suggest unlimited bandwidth. While usually traffic is not very high,
there may be cases that your hub will send or receive an anusual amount of traffic.
So, either go for a solution with unlimited data, or monitor your data usage and put
some safeguards in place.

You will also need RPC endpoints for Ethereum nodes on L2 OP Mainnet and L1 Mainnet. 
You can use a service like [Alchemy](https://www.alchemy.com/) or [Infura](https://www.infura.io/).

# Running your own Hub on your own hardware

My favourite option is running your own hub at home. I'm running two: 

- One of them on an old "Early 2009" Aluminum iMac Core 2 Duo with 8GB RAM and a
stock SSD.
- The other one on a Raspberry Pi4 with 8GB RAM, and 32GB (!!!) SD. This one is
sometimes struggling, and the available storage is bellow the recommended 20GB,
but... it works.

If you want to setup your own node, check out [Hubble](https://www.thehubble.xyz/intro/hubble.html).
The steps are quite straight forward.

# Running your own Hub on a general purpose cloud service provider

Using a VM on a cloud service like AWS or Google Cloud is not much different: Set up a VM, and follow [Hubble's](https://www.thehubble.xyz/intro/hubble.html) documentation.

There is also a nice video tutorial on how to [run Hubble on AWS](https://www.youtube.com/watch?v=rKoFJq_kHVc).

# Letting Neynar run your hub

[Neynar](https://neynar.com) specialises in Farcaster hosting services. 

Their plans start at $9/month and IMHO it's the easies way to get stared, especially if running Linux servers
is not your thing. Neynar runs your hub and you concentrate on building your app, or fool around with `fario` and the examples found in this 
repo. (That's why you are here, isn't it?)

