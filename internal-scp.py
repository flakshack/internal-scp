#!/usr/bin/env python
"""internal-scp.py
This script is intended to provide functionality similar to internal-sftp.exe
when using OpenSSH on a Windows Server, except that it limits SSH users to SCP
commands.

Why: The Windows OpenSSH server provides a secure SFTP-only functionality, but
does not provide a similar SCP-only capability. If you have a system that only
supports SCP, your only option is to allow it full SSH access, which presents
security issues (for example, by default the user could run SSH.EXE to connect
to other systems, perhaps bypassing a Firewall).

When configured as a "ForceCommand" in sshd_config, this script will restrict
a user to only running the Windows SCP.EXE command by replacing the SCP
from the passed command with the SCP.EXE full path (hardcoded below).

For easy management, it is suggested that you compile this script to EXE using
pyinstaller.  Install python and use these commands:
> pip install pyinstaller
> pyinstaller --onefile internal-scp.py
You will find internal-scp.exe in the "build" directory.

To implement it, copy the compiled internal-scp.exe file to the server and
apply it to the user in the sshd_config.  For example to limit user johndoe:

Match User johndoe
  ForceCommand c:/internal-scp/internal-scp.exe
  ChrootDirectory c:/sftp/%u

Note that you should ensure that permissions are set properly on this EXE to
prevent it from being overwritten by an SSH user.

Use of this code is at your own risk. Someone smarter than me may know how
to bypass it. Assume worst case scenario is user has full SSH access limited
by standard Windows permissions you've assigned.
"""

import os
import subprocess
import sys
import shlex

# Path to the trusted scp.exe on your Windows server
SCP_PATH = r"c:\Windows\System32\OpenSSH\scp.exe"

def main():
    # The command sent by the client is stored in an environment variable.
    ssh_command = os.environ.get("SSH_ORIGINAL_COMMAND")

    if not ssh_command:
        sys.stderr.write("Error: No command received.\n")
        sys.exit(1)

    try:
        # Use shlex to split the command into a list of tokens so we can strip
        # out the SCP part of the command.
        ssh_command = shlex.split(ssh_command, posix=False)
        scp_command = ssh_command[0]   # should contain "scp"
        scp_args = ssh_command[1:]     # remaining parameters
    except ValueError as e:
        sys.stderr.write(f"Error parsing scp command: {e}\n")
        sys.exit(1)

    # Check to make sure the command at least begins with SCP.
    if scp_command.lower() == "scp":
        try:
            # Run scp.exe with the original args. By default, subprocess.call
            # should avoid shell injection issues, only treating the remaining
            # text as an argument. Do not use shell=True here!
            new_command = [SCP_PATH] + scp_args
            result = subprocess.call(new_command)
            sys.exit(result)
        except Exception as e:
            sys.stderr.write(f"Error running scp: {e}\n")
            sys.exit(1)
    else:
        sys.stderr.write("Error: Only scp commands are permitted.\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
