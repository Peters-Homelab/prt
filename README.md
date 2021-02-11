# Parallel Remote Terminal

Excute the same command across multiple remote hosts in parallel.

## Abstract
In an attempt to streamline my own development process across multiple distributions, PRT was created to make testing shell scripts and binaries much faster and more intuitive. PRT lets a user define arbitrary pools of remote hosts, making it simple to brick sets of remote hosts into any number of abstraction layers (For instance grouping all Debian based systems into a pool). PRT is written 100% in python3 and makes no external calls your hosts ssh package.


## Install
To install PRT:
```bash
curl https://git.peters-homelab.com/Peters-Homelab/prt/raw/branch/master/build/install.sh | sudo bash
```
Once you have installed PRT, you will need to set up your connection pool files and remote access keys.

1. Run `prt --key_gen` to trigger the creation an RSA key that will be used to connect to the host in all your pools.
2. Create a yaml file containing an entry for each remote host in `~/.prt`. You can find an [example config here](https://git.peters-homelab.com/Peters-Homelab/prt/src/branch/master/build/example.yaml) 
3. Add your newly created `~/.prt/prt_rsa.pub` key to each of your remote hosts `~/.ssh/authorized_keys` file.


## Usage

- `-c, --command`: Defines the command you want to run on each remote host.
- `-p, --pool`: Spesifies the connection pool you want run on. (~/.prt/your_pool.yaml)
- `-k, --key_gen`: Triggers the generation of a universal PRT RSA key.


Example Command:
`prt -p xe -c "neofetch"`

![Demo Gif](https://i.imgur.com/JRYzjba.gif)
