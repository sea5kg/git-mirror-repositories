#!/usr/bin/env python3
# Copyright (c) 2024 Evgenii Sopov <mrseakg@gmail.com>

"""
Script for mirroring git-repositories
"""

import os
import sys
import subprocess
import yaml

print("Start mirroring git-repositories...")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH_YML = os.path.join(CURRENT_DIR, 'config.yml')
CONFIG = None

with open(CONFIG_PATH_YML, 'r') as file_config:
    try:
        CONFIG = yaml.safe_load(file_config)
    except yaml.YAMLError as exc:
        print(exc)

if CONFIG is None:
    sys.exit("Could not read " + CONFIG_PATH_YML)

print("Config path", CONFIG_PATH_YML)

# work dir
if "working_directory" not in CONFIG:
    sys.exit("Not found 'working_directory' in " + CONFIG_PATH_YML)
WORK_DIR = CONFIG["working_directory"]
if WORK_DIR[0] != '/':
    WORK_DIR = os.path.join(CURRENT_DIR, WORK_DIR)
WORK_DIR = os.path.normpath(WORK_DIR)
os.makedirs(WORK_DIR, exist_ok=True)
if not os.path.isdir(WORK_DIR):
    sys.exit("Could not create " + WORK_DIR)
print("Working directory", WORK_DIR)


def command_with_output(_command, print_to_console=True):
    """ run_command """
    _ret = ""
    _returncode = None
    if print_to_console:
        print("Run command: " + " ".join(_command))
    with subprocess.Popen(
        _command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=False
    ) as _proc:
        _returncode = _proc.poll()
        while _returncode is None:
            _returncode = _proc.poll()
            _line = _proc.stdout.readline()
            if _line:
                _line = _line.decode("utf-8")
                _ret += _line
                if print_to_console:
                    print(_line.rstrip())
        while _line:
            _line = _proc.stdout.readline()
            if _line:
                _line = _line.decode("utf-8")
                _ret += _line
                if print_to_console:
                    print(_line.rstrip())
            else:
                break
        if _returncode != 0:
            if print_to_console:
                print("ERROR: returncode " + str(_returncode))
    return _ret, _returncode


def git_current_branch():
    """ return current branch """
    _output, _retcode = command_with_output(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        print_to_console=False
    )
    return _output.strip()


if 'repositories' not in CONFIG:
    sys.exit("Not found 'repositories' in " + CONFIG_PATH_YML)

for _repoid in CONFIG["repositories"]:
    print("Start mirorring... ", _repoid)

    _repo = CONFIG["repositories"][_repoid]
    _repository_dir = os.path.join(WORK_DIR, _repoid)
    if not os.path.isdir(_repository_dir):
        os.makedirs(_repository_dir, exist_ok=True)
        if not os.path.isdir(_repository_dir):
            sys.exit("Could not creating " + _repository_dir)
        os.chdir(WORK_DIR)
        print("Cloning new repostiry")
        ret = os.system("git clone " + _repo["from"] + " " + _repoid)
        if ret != 0:
            sys.exit("Could not cloning to " + _repository_dir)
        os.chdir(CURRENT_DIR)
    os.chdir(_repository_dir)
    ret = os.system("git remote set-url origin " + _repo["from"])
    if ret != 0:
        sys.exit("Problem with git repository " + _repository_dir)
    ret = os.system("git pull -p")
    if ret != 0:
        sys.exit("Problem with git pull " + _repository_dir)

    # TODO keep information about mirroring
    _repository_info_dir = os.path.join(
        WORK_DIR,
        _repoid + ".mirroring_debug_info"
    )

    _output, _retcode = command_with_output(
        ["git", "branch", "-a", "-v"],
        print_to_console=False
    )

    _remotes_branches = []
    _local_branches = []
    _lines = _output.split("\n")
    for _line in _lines:
        _line = _line.strip()
        if _line == "":
            continue
        if _line.startswith("remotes/origin/"):
            _branch = _line.split(" ")[0]
            _branch = _branch[len("remotes/origin/"):]
            if _branch == "HEAD":
                continue
            _output, _retcode = command_with_output(
                ["git", "branch", "-a", "-v"],
                print_to_console=False
            )
            _remotes_branches.append(_branch)
        elif _line.startswith("*"):
            _current_branch = _line
            _current_branch = _current_branch[1:].strip().split(" ")[0]
            _local_branches.append(_current_branch)
        else:
            _local_branches.append(_line)

    print("_current_branch", _current_branch)
    print("_remotes_branches", _remotes_branches)
    print("_local_branches", _local_branches)

    for _branch in _remotes_branches:
        if _branch != git_current_branch():
            _ret = os.system("git checkout " + _branch)
            print(_ret)
        _ret = os.system("git reset --hard origin/" + _branch)
        print(_ret)

    # print(_output)
    # todo get list of branches and tags - remember

    print("Done with", _repoid)
    os.chdir(CURRENT_DIR)
