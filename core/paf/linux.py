#! /usr/bin/env python3
import re
import os
import sys
import subprocess
from .file import read_file


############
# Linux System Commands
######

def am_i_root():
    '''
    Checks if python was run with sudo or as root.
    Returns True if root and False if userspace.
    '''
    if os.getuid() == 0:
        return True
    else:
        return False


def list_normal_users():
    '''
    Get info about every normal users.
    '''
    usr_list = set()

    for x in read_file('/etc/login.defs'):
        if x.startswith('UID_MIN'):
            min_uid = int(x.split('\t')[-1].strip())
        if x.startswith('UID_MAX'):
            max_uid = int(x.split('\t')[-1].strip())
    usr_range = range(min_uid, max_uid + 1)

    for x in read_file('/etc/passwd'):
        entry = tuple(x.split(':'))
        if int(entry[2]) in usr_range:
            usr_list.add(entry)

    return usr_list


############
# File System Commands
######

def rm_file(file_path, sudo=False):
    '''
    Uses os.system() to remove files using standard *nix commands.
    The main advatage over os submodule is support for sudo.
    '''
    if sudo is True:
        s = 'sudo '
    elif sudo is False:
        s = ''
    else:
        sys.exit('Error: Sudo Must be True/False!')

    os.system(s + '/bin/rm -f ' + escape_bash_input(file_path))


def mk_dir(dir_path, sudo=False):
    '''
    Uses os.system() to make a directory using standard *nix commands.
    The main advatage over os submodule is support for sudo.
    '''
    if sudo is True:
        s = 'sudo '
    elif sudo is False:
        s = ''
    else:
        sys.exit('Error: Sudo Must be True/False!')

    os.system(s + "/bin/mkdir -p " + escape_bash_input(dir_path))


def rm_dir(dir_path, sudo=False):
    '''
    Uses os.system() to remove a directory using standard *nix commands.
    The main advatage over os submodule is support for sudo.
    '''
    if sudo is True:
        s = 'sudo '
    elif sudo is False:
        s = ''
    else:
        sys.exit('Error: Sudo Must be True/False!')

    os.system(s + '/bin/rm -fr ' + escape_bash_input(dir_path))


def basename(path):
    '''
    Provides faster file name trim than os.basename()
    '''
    return path.split('/')[-1]


def basenames(file_list):
    '''
    Returns a list of unique file names. Will remove duplicates names.
    Provides faster file name trim than looping with os.basename()
    '''
    return {p.split('/')[-1] for p in file_list}


############
# Terminal
######

def escape_bash_input(astr):
    '''
    Uses regex subsitution to safely escape bash input.
    '''
    return re.sub("(!| |\$|#|&|\"|\'|\(|\)|\||<|>|`|\\\|;)", r"\\\1", astr)


def sed_uncomment_line(pattern, file_path, sudo):
    '''
    Uncomments lines using sed. This can safely be run over a file multiple
    times without adverse effects. This is ungodly helpful when modifing
    linux config files.
    '''
    if sudo is True:
        s = 'sudo '
    elif sudo is False:
        s = ''
    else:
        sys.exit('Error: Sudo Must be True/False!')

    os.system(s + "/bin/sed -e'/" + pattern + "/s/^#//g' -i " + escape_bash_input(file_path))


def sed_comment_line(pattern, file_path, sudo):
    '''
    Comments lines using sed. This can safely be run over a file multiple
    times without adverse effects. This is ungodly helpful when modifing
    linux config files.
    '''
    if sudo is True:
        s = 'sudo '
    elif sudo is False:
        s = ''
    else:
        sys.exit('Error: Sudo Must be True/False!')

    os.system(s + "/bin/sed -e'/" + pattern + "/s/^#*/#/g' -i " + escape_bash_input(file_path))


############
# File and Folder Permissions
######

def get_permissions(basedir, typ):
    '''
    For some reason python has no simple inbuilt way to get file or folder permissions
    without changing the permission. This is gross but it works.
    Returns set of tuples in format (path, permissions, owner, group)
    '''
    # Fetch Folder Permissions
    if typ == 'files':
        typ = 'f'
    elif typ == 'folders':
        typ = 'd'
    else:
        sys.exit('Error: Type Must Be `Files` or `Folders`!')

    cmd = str('/usr/bin/find ' + escape_bash_input(basedir) + ' -type ' + typ + ' -exec ls -d -l */ {} +')
    raw = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    out = str(raw.communicate())[3:]
    out = out.split('\n')
    out = set(out[0].split('\\n')[:-1])

    # Parse Perms
    perms = set()
    for x in out:
        s = x.split(' ')
        s = ' '.join([x for x in s if x != '']).split(' ', 8)
        s = (s[8].replace("'", "").strip(), s[0].strip(), s[2].strip(), s[3].strip())
        if s[0].startswith('/'):
            perms.add(s)

    return perms


def perm_to_num(symbolic):
    '''
    Convert symbolic permission notation to numeric notation.
    '''
    perms = {
            '---': '0',
            '--x': '1',
            '-w-': '2',
            '-wx': '3',
            'r--': '4',
            'r-x': '5',
            'rw-': '6',
            'rwx': '7'
        }

    # Trim Lead If It Exists
    if len(symbolic) == 10:
        symbolic = symbolic[1:]

    # Parse Symbolic to Numeric
    x = (symbolic[:-6], symbolic[3:-3], symbolic[6:])
    numeric = perms[x[0]] + perms[x[1]] + perms[x[2]]
    return numeric
