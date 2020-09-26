#!/usr/bin/env python3

import os
import sys
import paf
import yaml
import paramiko
import argparse
import itertools
import multiprocessing as mp
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

    mand = {'NAME', 'USER', 'IP', 'PORT'}
    error = 0

    for host in hosts:
        x = hosts[host]
        for val in mand:
            if val not in x:
                print('Error: Host ' + host + ' Is Missing The Field "' + val + '"!')
                error += 1
    if error == 0:
        print('Successfully Loaded Pool of Hosts')
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
        print('PRT Pool Key Found')
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
    """
    """
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
                con_info[1]['IP'],
                port=con_info[1]['PORT'],
                username=con_info[1]['USER'],
                key_filename=str(base + 'prt_rsa.key')
            )

        else:
            client.connect(
                con_info[1]['IP'],
                port=con_info[1]['PORT'],
                username=con_info['USER'],
                key_filename=str(Path.home()) + 'prt_rsa.key',
                gss_auth=UseGSSAPI,
                gss_kex=DoGSSAPIKeyExchange,
            )

        con_status = str('Connection Succeeded')
        stdin, stdout, stderr = client.exec_command(command)
        results_dict = {
            'name': con_info[0],
            'uname': con_info[1]['NAME'],
            'status': con_status,
            'stdout': [x.replace('\n', '') for x in stdout.readlines()],
            'stderr': [x.replace('\n', '') for x in stderr.readlines()]
        }
        client.close()

    except Exception as error:
        con_status = str("Connection Failed : PRT Caught exception(%s: %s" % (error.__class__, error) + ')')
        results_dict = {
            'name': con_info[0],
            'uname': con_info[1]['NAME'],
            'status': con_status,
            'stdout': [],
            'stderr': []
        }
        try:
            client.close()
        except Exception:
            pass

    return results_dict


def run_pool(conf, usr_cmd, print_out):
    """
    """
    # Setup for Connection
    hosts = read_hosts_yaml(conf)
    gen_prt_key()

    # Run a Pool of Threads for Each Connection
    print('Starting Parallel Connection Pool For ' + str(len(hosts)) + ' Remote Hosts...')
    x = [(k, v) for k, v in hosts.items()]
    with mp.Pool(processes=len(hosts)) as pool:
        mp_out = pool.starmap(run_on_host, zip(x, itertools.repeat(usr_cmd)))

    # Print Results for User
    umax = max(len(z['uname']) for z in mp_out)
    cmax = max(len((' ').join(str(z['status']).split(' ')[:2])) for z in mp_out)
    print()

    for x in mp_out:
        cstat = (' ').join(str(x['status']).split(' ')[:2])
        pad1 = ' '*(umax - len(x['uname']))
        pad2 = ' '*(cmax - len(cstat))

        if x['stderr']:
            cmd = 'Command Returned An Error'
        elif x['stdout']:
            cmd = 'Command Ran Successfully'
        else:
            cmd = 'Command Returned NO Output'

        out = x['uname'] + ':  ' + pad1 + cstat + '  ' + pad2 + cmd
        print(out)

    # Output Results File
    print()
    if print_out is True:
        if any(x['stdout'] for x in mp_out):
            nmax = max(len(z) for z in x['stdout'] for x in mp_out)
            nmin = min(len(z) for z in x['stdout'] for x in mp_out)
            pad = round((nmax - nmin)/2)
            if pad < 5:
                pad = 5

        for x in mp_out:
            if x['stdout']:
                print('='*pad + ' ' + x['uname'] + ' ' + '='*pad)
                print()
                for z in x['stdout']:
                    print(z)
                print()


run_pool('xe', 'cat /etc/*release', True)
