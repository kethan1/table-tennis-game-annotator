import re
import os
import argparse
import platform
import subprocess


parser = argparse.ArgumentParser(description="Run different commands based on the OS")
parser.add_argument("--windows", help="Command to run on Windows", required=True)
parser.add_argument("--linux", help="Command to run on Linux", required=True)
parser.add_argument("--macos", help="Command to run on MacOS, defaults to Linux command")
args = parser.parse_args()

if args.macos is None:
    args.macos = args.linux


def preprocess(string):
    split = re.findall(r"\{(.*?)\}", string)
    final_sub = {}
    for sub in split:
        sub_split = sub.split(":")
        if sub_split[0] == "env":
            final_sub[sub] = os.environ[sub_split[1]]
    for old, new in final_sub.items():
        string = string.replace("{" + old + "}", new)
    return string


args.windows = preprocess(args.windows)
args.linux = preprocess(args.linux)
args.macos = preprocess(args.macos)

if platform.system() == "Windows":
    popen_kwargs = {"stdin": subprocess.PIPE}
    proc = subprocess.Popen(args.windows, **popen_kwargs, shell=True)
elif platform.system() == "Linux":
    popen_kwargs = {"stdin": subprocess.PIPE}
    proc = subprocess.Popen(args.linux, **popen_kwargs, shell=True)
elif platform.system() == "Darwin":
    popen_kwargs = {"stdin": subprocess.PIPE}
    proc = subprocess.Popen(args.macos, **popen_kwargs, shell=True)

proc.wait()
