This script is intended to provide functionality similar to internal-sftp.exe
when using OpenSSH on a Windows Server, except that it limits SSH users to SCP
commands. Note that as it only accepts SCP commands, it is not fully compatible
with tools like WinSCP which uses other shell commands (for example to get
directory lists). 

Why: The Windows OpenSSH server provides a secure SFTP-only functionality, but
does not provide a similar SCP-only capability. If you have a system that only
supports SCP, your only option is to allow it full SSH access, which presents
security issues (for example, by default the user could run SSH.EXE to connect
to other systems, perhaps bypassing a firewall).

When configured as a "ForceCommand" in sshd_config, this script will restrict
a user to only running the Windows SCP.EXE command by replacing the SCP
from the passed command with the SCP.EXE full path (which is hardcoded).

For easy management, it is suggested that you compile this script to EXE using
pyinstaller.  Install python and use these commands:

pip install pyinstaller\
pyinstaller --onefile internal-scp.py

You will find internal-scp.exe in the "dist" directory.

To implement it, copy the compiled internal-scp.exe file to the server and
apply it to the user in the sshd_config.  For example to limit user johndoe:

Match User johndoe\
&nbsp; ForceCommand c:/internal-scp/internal-scp.exe\
&nbsp; ChrootDirectory c:/sftp/%u

**Note the launched SCP command itself is not limited to the ChrootDirectory from a 
security perspective.**  While the user is limited to running SCP.EXE, this still
allows the user to access any file on the host to which they have normal NTFS 
permissions (read & write).  In particular, ensure that permissions are set 
properly on this EXE to prevent it from being overwritten by the SSH user.
The SCP command could be used for network access to other servers as a proxy for 
data exfiltration (possibly past a firewall).  

**Use of this code is at your own risk.** 
You should assume the user has full SSH access limited by standard Windows 
permissions you've assigned. A proper implementation would include firewall access
controls, anti-malware software, application whitelisting, file access auditing, 
logging, strict file permissions, and limited user rights.
