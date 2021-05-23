#!/usr/bin/env bash
osname=$(cat /etc/*release | grep -Pi '^ID=' | head -1 | cut -c4- | sed -e 's/^"//' -e 's/"$//')

## DEBIAN
if [[ $osname == 'ubuntu' ]] || [[ $osname == 'debian' ]]; then
  # Install Dependencies
  apt --yes install python3 python-yaml python3-paramiko

## CENTOS
elif [[ $osname == 'centos' ]] || [[ $osname == 'fedora' ]]; then
  # Install Dependencies
  yum -y install python38 python38-pyyaml python3-paramiko

## ARCH
elif [[ $osname == 'arch' ]] || [[ $osname == 'manjaro' ]]; then
  # Install Dependencies
  pacman -S --noconfirm --needed python python-yaml python-paramiko

## NOT SUPPORTED
else
  echo $osname Is Not Supported!
  exit
fi

sudo git clone --recurse-submodules https://github.com/Peters-Homelab/prt.git /opt/prt
sudo ln -sf /opt/prt/core/prt.py /usr/bin/prt

echo ''
echo Finished Installing PRT!
echo ''