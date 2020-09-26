#!/usr/bin/env python3

import os
import sys
import paf
import yaml
import paramiko
import argparse
from pathlib import Path


def read_hosts_yaml(conf):
    """
    Read and parse yaml file containing a pool of remote hosts.
    """
    base = str(str(Path.home()) + '/.prt/')
    conf_path = str(base + paf.escape_bash_input(conf) + '.yaml')
    if not os.path.exists(conf_path):
        sys.exit('Error: No Config File Named "' + conf + '" Found in "' + base + '"!')

    with open(conf_path) as file:
        hosts = yaml.full_load(file)

    mand = {'NAME', 'USER', 'IP', 'PORT', 'BAD'}
    error = 0

    for host in hosts:
        x = hosts[host]
        for val in mand:
            if val not in x:
                print('Error: Host ' + host + ' Is Missing The Field "' + val + '"!')
                error += 1
    if error == 0:
        return hosts
    else:
        print('')
        sys.exit(str(error) + ' Errors Were Found in ' + conf_path + '!')


def gen_prt_key():
    """
    Generate public and private keys for PRT.
    """
    base = str(str(Path.home()) + '/.prt/')
    key_path = base + 'prt_rsa.key'
    pub_path = base + 'prt_rsa.pub'

    if not os.path.exists(base):
        os.makedirs(base)

    if os.path.exists(key_path):
        print('PRT Key Found')
        return

    else:
        print('No PRT Key Found!')
        print('Generating RSA Key...')
        key = paramiko.RSAKey.generate(8192)
        print('Exporting Private Key...')
        key.write_private_key_file(key_path)

        print('Exporting Public Key...')
        with open(pub_path, "w") as public:
            public.write("%s %s" % (key.get_name(), key.get_base64()))

        print('You Must Now Copy The Newly Generated Public Key To Each Machine In Your Host Pool.')
        sys.exit('Add The Output Of `cat ' + pub_path + '` To Each Remote Hosts "~/.ssh/authorized_keys" File!')


def run_on_host(con_info, command):
    ''' '''
    base = str(str(Path.home()) + '/.prt/')
    # Paramiko client configuration
    paramiko.util.log_to_file(base + "prt_paramiko.log")
    UseGSSAPI = (paramiko.GSS_AUTH_AVAILABLE)
    DoGSSAPIKeyExchange = (paramiko.GSS_AUTH_AVAILABLE)

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()

        if not UseGSSAPI and not DoGSSAPIKeyExchange:
            client.connect(
                con_info['IP'],
                port=con_info['PORT'],
                username=con_info['USER'],
                key_filename=str(base + 'prt_rsa.key')
            )

        else:
            client.connect(
                con_info['IP'],
                port=con_info['PORT'],
                username=con_info['USER'],
                key_filename=str(Path.home()) + 'prt_rsa.key',
                gss_auth=UseGSSAPI,
                gss_kex=DoGSSAPIKeyExchange,
            )

        con_status = str('Connection Success')
        stdin, stdout, stderr = client.exec_command(command)
        results_dict = {
            'status': con_status,
            'stdout': [x.replace('\n', '') for x in stdout.readlines()],
            'stderr': [x.replace('\n', '') for x in stderr.readlines()]
        }
        client.close()

    except Exception as error:
        con_status = str("Connection Error: PRT Caught exception( %s: %s" % (error.__class__, error) + ' )')
        results_dict = {
            'status': con_status,
            'stdout': 'NONE',
            'stderr': 'NONE'
        }
        try:
            client.close()
        except Exception:
            pass

    return results_dict


def run_pool(conf, usr_cmd):
    ''' '''
    hosts = read_hosts_yaml(conf)




