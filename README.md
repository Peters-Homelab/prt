# Parallel Remote Terminal

Excute commands across multiple remote terminals in parallel

## Abstract
In an attempt to streamline the development process across multiple distributions, PRT was created to make testing various scripts and binaries much faster and more intuitive. PRT lets a user define multiple pools of remote hosts and sends them the same commands in parrallel.


## Usage
To install PRT simply use the install script:
```bash
curl https://raw.githubusercontent.com/JustinTimperio/prt/master/build/install.sh | sudo bash
```
Once you have installed PRT, you will need to set up you connection pools and remote access keys.
1. Create a list of yaml file containing a entry for each remote host. You can find an [example config here](https://github.com/JustinTimperio/prt/blob/master/build/example.yaml) 
2. Place your newly created yaml file in `~/.prt`. (This directory won't exist by default)
3. Run PRT with your yaml file. `prt -p your_yaml -c your_command` This will trigger the creation of a new RSA key that will be used for all your pools
4. Add your newly created RSA.pub key to each of your remote hosts `~/.ssh/authorized_keys` file.
5. You are now fully setup!

![Demo Gif](https://i.imgur.com/tJpVLu0.gif)
