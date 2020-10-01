#!/usr/bin/env python3

# Core Modules
import re
import os
import sys
import argparse
import itertools
import multiprocessing as mp
from pathlib import Path

# External Modules
import paf
import yaml
import paramiko

base = str(str(Path.home()) + '/.prt/')


def read_hosts_yaml(conf):
    """
    Read and parse yaml file containing a pool of remote hosts.
    """
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


def run_pool(conf, usr_cmd):
    """
    Runs a Pool of Commands and returns the results to user.
    """
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    out_file = base + conf + '_output.txt'

    def parse_line(line):
        with open(out_file, 'a') as f:
            f.write("%s\n" % ansi_escape.sub('', line))

    # Setup for Connections
    hosts = read_hosts_yaml(conf)
    gen_prt_key()
    paf.start_log('Pool "' + conf + '"', out_file)
    parse_line('')

    # Run a Pool of Threads for Each Connection
    print('Starting Pool of ' + str(len(hosts)) + ' Parallel Connections...')
    x = [(k, v) for k, v in hosts.items()]
    with mp.Pool(processes=len(hosts)) as pool:
        mp_out = pool.starmap(run_on_host, zip(x, itertools.repeat(usr_cmd)))

    # Print Results for User
    umax = max(len(z['uname']) for z in mp_out)
    cmax = max(len((' ').join(str(z['status']).split(' ')[:2])) for z in mp_out)
    print()

    # Create Summary
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
        parse_line(out)

    # Determines How Wide to Make Bars
    lens = set()
    for x in mp_out:
        for z in x['stdout']:
            lens.add(len(ansi_escape.sub('', z)))
        for r in x['stderr']:
            lens.add(len(ansi_escape.sub('', r)))

    lmax = max(lens)
    lmin = min(lens)
    pad = round((lmax - lmin)/2)
    if pad < 10:
        pad = 10

    # Print the Actual Output
    for x in mp_out:
        if x['stdout']:
            out = ('\n' + '='*pad + ' ' + x['uname'] + ' ' + '='*pad + '\n')
            print(out)
            parse_line(out)
            for z in x['stdout']:
                print(z)
                parse_line(z)

        if x['stderr']:
            out = ('\n' + '='*pad + ' ' + x['uname'] + ' ' + '='*pad + '\n')
            print(out)
            parse_line(out)
            for z in x['stderr']:
                print(z)
                parse_line(z)

        if x['status'].startswith('Connection Failed'):
            out = ('\n' + '='*pad + ' ' + x['uname'] + ' ' + '='*pad + '\n')
            print(out)
            parse_line(out)
            print(x['status'])
            parse_line(x['status'])


    parse_line('')
    paf.end_log('Pool "' + conf + '"', out_file)
    print('')
    print('Output Is Stored In ' + out_file)


# Argument Parser
parser = argparse.ArgumentParser(description="A tool for running commands in parallel across multiple remote hosts.")

parser.add_argument("-c", "--command", metavar='REMOTE COMMAND',
                    help="Print the output from each successful command.")
parser.add_argument("-p", "--pool", metavar='POOL_YAML',
                    help="Select the pool yaml file you want to use.")
parser.add_argument("-v", "--version", action='store_true',
                    help="Display PRT's version information.")
args = parser.parse_args()

# Process Arguments
if args.version:
    print('PRT Version: 1.0.0')

if args.command:
    if args.pool:
        run_pool(args.pool, args.command)
    else:
        print('Error: No Pool Defined for Command to Run On!')
