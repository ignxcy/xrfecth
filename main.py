#!/usr/bin/env python

from platform import system, machine, uname
import subprocess
import shutil
import os

# Colors
reset = "\033[0m"
magenta = "\033[1;35m"
green = "\033[1;32m"
white = "\033[1;37m"
blue = "\033[1;34m"
red = "\033[1;31m"
black = "\033[1;40;30m"
yellow = "\033[1;33m"
cyan = "\033[1;36m"
bgyellow = "\033[1;43;33m"
bgwhite = "\033[1;47;37m"

# Get the kernel
kernel = system()

# Get the init
def get_init():
    if kernel == "Android":
        return 'init.rc'
    elif kernel == "Darwin":
        return 'launchd'
    elif 'systemd' in subprocess.getoutput('pidof -q systemd'):
        return 'systemd'
    elif subprocess.run(['test', '-f', '/sbin/openrc']).returncode == 0:
        return 'openrc'
    elif subprocess.run(['test', '-f', '/sbin/dinit']).returncode == 0:
        return 'dinit'
    else:
        return subprocess.getoutput("cut -d ' ' -f 1 /proc/1/comm")

# Get count of packages installed
def get_pkg_count():
    package_managers = ['xbps-install', 'apk', 'port', 'apt', 'pacman', 'nix', 'dnf', 'rpm', 'emerge', 'eopkg']
    for package_manager in package_managers:
        if shutil.which(package_manager):
            if package_manager == 'xbps-install':
                return int(subprocess.getoutput('xbps-query -l | wc -l'))
            elif package_manager == 'apk':
                return int(subprocess.getoutput('apk search | wc -l'))
            elif package_manager == 'apt':
                if kernel != 'Darwin':
                    return int(subprocess.getoutput("echo $(( $(apt list --installed 2>/dev/null | wc -l) - 1 ))"))
                else:
                    return 0
            elif package_manager == 'pacman':
                return int(subprocess.getoutput('pacman -Q | wc -l'))
            elif package_manager == 'nix':
                return int(subprocess.getoutput('nix-env -qa --installed \'*\' | wc -l'))
            elif package_manager == 'dnf':
                return int(subprocess.getoutput('dnf list installed | wc -l'))
            elif package_manager == 'rpm':
                return int(subprocess.getoutput('rpm -qa | wc -l'))
            elif package_manager == 'emerge':
                return int(subprocess.getoutput('qlist -I | wc -l'))
            elif package_manager == 'port':
                return int(subprocess.getoutput('port installed 2>/dev/null | wc -l | awk \'NR==1{print $1}\''))
            elif package_manager == 'eopkg':
                return int(subprocess.getoutput('eopkg li | wc -l'))

# Get count of snaps installed
# Get count of snaps installed
def get_snap_count():
    if shutil.which('snap'):
        count = subprocess.getoutput("snap list | wc -l")
        return int(count) - 1  # Adjusting for the header line in 'snap list'
    return 0

# Get count of flatpaks installed
def get_flatpak_count():
    if shutil.which('flatpak'):
        count = subprocess.getoutput("flatpak list | wc -l")
        return int(count)
    return 0

# Get count of brews(formulas + casks) installed
def get_brew_count():
    if shutil.which('brew'):
        formula_count = subprocess.getoutput("brew list --formula | wc -l | awk 'NR==1{print $1}'")
        cask_count = subprocess.getoutput("brew list --casks | wc -l | awk 'NR==1{print $1}'")
        return int(formula_count) + int(cask_count)
    return 0

# Get package information formatted
def get_package_info():
    pkg_count = get_pkg_count()
    snap_count = get_snap_count()
    flatpak_count = get_flatpak_count()
    brew_count = get_brew_count()

    if pkg_count != 0:
        result = f"{pkg_count}"
        if snap_count != 0:
            result += f" ({snap_count} snaps"
            if flatpak_count != 0:
                result += f", {flatpak_count} flatpaks)"
            else:
                result += ")"
        elif flatpak_count != 0:
            result += f" ({flatpak_count} flatpaks)"
        elif brew_count != 0:
            cask_count = int(subprocess.getoutput('brew list --casks | wc -l | awk \'NR==1{print $1}\''))
            formula_count = int(subprocess.getoutput('brew list --formula | wc -l | awk \'NR==1{print $1}\''))
            result += f", {brew_count} brews ({formula_count} formulas & {cask_count} casks)"
        return result
    elif snap_count != 0:
        return f"{snap_count} snaps"
    elif flatpak_count != 0:
        return f"{flatpak_count} flatpaks"
    elif brew_count != 0:
        cask_count = int(subprocess.getoutput('brew list --casks | wc -l | awk \'NR==1{print $1}\''))
        formula_count = int(subprocess.getoutput('brew list --formula | wc -l | awk \'NR==1{print $1}\''))
        return f"{brew_count} brews ({formula_count} formulas & {cask_count} casks)"
    else:
        return "Unknown"

# Get distro name
def get_distro_name():
    if kernel == 'Android':
        return 'Android'
    elif kernel == 'Darwin':
        return f"macOS {uname()[0]} {subprocess.getoutput('sw_vers -productVersion')}"
    else:
        return subprocess.getoutput("awk -F '\"' '/PRETTY_NAME/ { print $2 }' /etc/os-release")

# Get root partition space used
def get_storage_info():
    try:
        if kernel == 'Android':
            _MOUNTED_ON = "/data"
            _GREP_ONE_ROW = subprocess.getoutput("df -h | grep " + _MOUNTED_ON)
            _SIZE = _GREP_ONE_ROW.split()[1]
            _USED = _GREP_ONE_ROW.split()[2]
            return f"{_USED}B / {_SIZE}B"
        elif kernel == 'Darwin':
            total_size = subprocess.getoutput("df -Hl | grep -w '/' | awk '{print $2}'")
            free_size = subprocess.getoutput("df -Hl | grep -w '/' | awk '{print $4}'")
            used_size = int(total_size[:-1]) - int(free_size[:-1])
            return f"{used_size}G / {total_size}"
        else:
            df_output = subprocess.getoutput("df -h --output=used,size / | awk 'NR == 2 { print $1\" / \"$2 }'")
            return df_output
    except Exception as e:
        print(f"Error getting storage info: {e}")
        return "Unknown"


# Get Memory usage
def get_mem():
    if kernel == 'Darwin':
        total_mem = int(subprocess.getoutput(
            "sysctl -a | awk '/hw./' | awk '/mem/' | awk 'NR==1{print $2}'")) // (2 ** 20)
        used_mem = int(subprocess.getoutput("vm_stat | grep -E 'Pageouts:' | awk 'NR==1{print $2}'"))
        return f"{used_mem} / {total_mem} MB"
    else:
        free_mem = subprocess.getoutput("free --mega | awk 'NR == 2 { print $3\" / \"$2\" MB\" }'")
        return free_mem

# Get uptime
def get_uptime():
    if kernel == 'Darwin':
        up = subprocess.getoutput("uptime | awk 'NR==1{print $3}'")
        return f" {up[:-1]}"
    else:
        return subprocess.getoutput("uptime -p | sed 's/up//'")

# Get DE/WM
def get_de_wm():
    wm = os.environ.get('XDG_CURRENT_DESKTOP', '')
    if not wm and 'DISPLAY' in os.environ and shutil.which('xprop'):
        id_cmd = "xprop -root -notype _NET_SUPPORTING_WM_CHECK 2>/dev/null"
        id = subprocess.getoutput(id_cmd).split()[-1]
        wm_cmd = f"xprop -id {id} -notype -len 100 -f _NET_WM_NAME 8t 2>/dev/null | grep '^_NET_WM_NAME' | cut -d\" -f 2"
        wm = subprocess.getoutput(wm_cmd)
    
    non_ewmh_wms = ['sway', 'kiwmi', 'wayfire', 'sowm', 'catwm', 'fvwm', 'dwm', '2bwm', 'monsterwm', 'tinywm', 'xmonad']
    if not wm or wm == 'LG3D':
        for current_wm in non_ewmh_wms:
            if subprocess.run(['pgrep', '-x', current_wm, '2>/dev/null']).returncode == 0:
                wm = current_wm
                break

    return wm if wm else 'unknown'

print("               ")

if kernel == 'Android':
    print(f"               {cyan}phone{white}  {subprocess.getoutput('getprop ro.product.brand')} {subprocess.getoutput('getprop ro.product.model')}")
    
print(f"               {magenta}os{white}     {get_distro_name()} {uname().machine}")
print(f"               {green}ker{white}    {uname().release}")
print(f"     {white}•{black}_{white}•{reset}       {yellow}pkgs{white}   {get_package_info()}")
print(f"     {black}oo{reset}|       {blue}sh{white}     {os.path.basename(os.getenv('SHELL'))}")
print(f"    {yellow}/\{reset}'\\       {red}ram{white}    {get_mem()}")
print(f"   {bgyellow}({reset}\_;/{bgyellow}){reset}      {magenta}init{white}   {get_init()}")

if 'DISPLAY' in os.environ:
    print(f"               {green}de/wm{white}  {get_de_wm()}")

print(f"               {yellow}up{white}    {get_uptime()}")
print(f"               {red}disk{white}   {get_storage_info()}")
print("               ")

if kernel != 'Android' and kernel != 'Darwin':
    print(f"        {red}󰮯  {blue}󰊠  {green}󰊠  {yellow}󰊠  {cyan}󰊠  {reset}")

print("               \033[0m")
