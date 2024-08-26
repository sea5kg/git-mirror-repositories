#!/usr/bin/env python3
# Copyright (c) 2024 Evgenii Sopov <mrseakg@gmail.com>

"""
Script for mirroring git-repositories
"""

import os
import sys
import subprocess
import yaml

print("""
    Welcome to script for mirorring git repositories
""")

print(" * Start mirroring git-repositories...")

# CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CURRENT_DIR = os.getcwd()
CONFIG_PATH_YML = os.path.join(CURRENT_DIR, 'config.yml')
CONFIG = None

with open(CONFIG_PATH_YML, 'r') as file_config:
    try:
        CONFIG = yaml.safe_load(file_config)
    except yaml.YAMLError as exc:
        print(exc)

if CONFIG is None:
    sys.exit("\nFAILED: Could not read " + CONFIG_PATH_YML)

if 'repositories' not in CONFIG:
    CONFIG['repositories'] = {}

print(" * Config path", CONFIG_PATH_YML)

# work dir
if "working_directory" not in CONFIG:
    sys.exit("\nFAILED: Not found 'working_directory' in " + CONFIG_PATH_YML)
WORK_DIR = CONFIG["working_directory"]
if WORK_DIR[0] != '/':
    WORK_DIR = os.path.join(CURRENT_DIR, WORK_DIR)
WORK_DIR = os.path.normpath(WORK_DIR)
os.makedirs(WORK_DIR, exist_ok=True)
if not os.path.isdir(WORK_DIR):
    sys.exit("\nFAILED: Could not create " + WORK_DIR)
print(" * Working directory", WORK_DIR)

print(" * Searching another configs in ", CURRENT_DIR)
for _file in os.listdir(CURRENT_DIR):
    if _file.startswith("config_") and _file.endswith(".yml"):
        TMP_CONFIG_PATH = os.path.join(CURRENT_DIR, _file)
        print(" * Reading:", TMP_CONFIG_PATH)
        TMP_CONFIG = None
        with open(TMP_CONFIG_PATH, 'r') as file_config:
            try:
                TMP_CONFIG = yaml.safe_load(file_config)
            except yaml.YAMLError as exc:
                print(exc)
                print("SKIP: Could not read file ", TMP_CONFIG)
        if 'repositories' not in TMP_CONFIG:
            print("SKIP: Did not found 'repositories' in ", TMP_CONFIG)
            continue
        for _repo in TMP_CONFIG['repositories']:
            if _repo in CONFIG['repositories']:
                print("WARNING: Defined again '" + _repo + "' in ", TMP_CONFIG)
                continue
            CONFIG['repositories'][_repo] = TMP_CONFIG['repositories'][_repo]


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


class FolderSwitcher:
    """
        Change work directory to specify folder
        And on exit change back work directory
    """
    def __init__(self, new_dir):
        self.__prev = os.getcwd()
        os.chdir(new_dir)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # print("Switch to " + self.__prev)
        os.chdir(self.__prev)


def git_current_branch(_repository_dir):
    """ return current branch """
    with FolderSwitcher(_repository_dir) as _:
        _output, _retcode = command_with_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            print_to_console=False
        )
        return _output.strip()


def git_pull(_repository_dir):
    """ git pull -p """
    with FolderSwitcher(_repository_dir) as _:
        _output, _retcode = command_with_output(
            ["git", "pull", "-p"],
            print_to_console=False
        )
        if _retcode != 0:
            sys.exit("\nFAILED: Problem with git pull " + _repository_dir)


def git_remote_set_url_origin(_repository_dir, _url):
    """ git remote set-url origin """
    with FolderSwitcher(_repository_dir) as _:
        _output, _retcode = command_with_output(
            ["git", "remote", "set-url", "origin", _url],
            print_to_console=False
        )
        if _retcode != 0:
            sys.exit(
                "\nFAILED: Problem with git remote set-url origin for: " +
                _repository_dir
            )


def git_reset_hard(_repository_dir, _branch):
    """ git reset --hard origin/... """
    with FolderSwitcher(_repository_dir) as _:
        _output, _retcode = command_with_output(
            ["git", "reset", "--hard", "origin/" + _branch],
            print_to_console=False
        )
        if _retcode != 0:
            sys.exit("\nFAILED: Could not reset repository branch! ;(")


def git_push_force(_repository_dir, _):
    """ git push -f """
    with FolderSwitcher(_repository_dir) as _:
        _output, _retcode = command_with_output(
            ["git", "push", "-f"],
            print_to_console=False
        )
        if _retcode != 0:
            sys.exit(
                "\nFAILED: Could not reset repository branch! ;(\n"
                + _output
            )


def git_switch_branch(_repository_dir, _branch):
    """ git checkout ... """
    with FolderSwitcher(_repository_dir) as _:
        if _branch != git_current_branch(_repository_dir):
            _output, _retcode = command_with_output(
                ["git", "checkout", _branch],
                print_to_console=False
            )
            if _retcode != 0:
                sys.exit(
                    "\nFAILED: Could not switch branch ;(\n" +
                    _output
                )


def git_push_origin_tags(_repository_dir):
    """ git push origin tags """
    with FolderSwitcher(_repository_dir) as _:
        _output, _retcode = command_with_output(
            ["git", "push", "origin", "--tags"],
            print_to_console=False
        )
        if _retcode != 0:
            sys.exit("\nFAILED: Could not push tags ;(\n" + _output)


if 'repositories' not in CONFIG:
    sys.exit("Not found 'repositories' in " + CONFIG_PATH_YML)


for _repoid in CONFIG["repositories"]:
    _repo = CONFIG["repositories"][_repoid]
    if 'enabled' in _repo and not _repo['enabled']:
        print(" -> Skip mirorring repo:", _repoid)
        continue

    print(" -> Start mirorring repo:", _repoid)
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

    git_remote_set_url_origin(_repository_dir, _repo["from"])
    git_pull(_repository_dir)

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
            # current branch
            _line = _line[1:].strip().split(" ")[0]
            _local_branches.append(_line)
        else:
            _local_branches.append(_line)

    # print("_remotes_branches", _remotes_branches)
    # print("_local_branches", _local_branches)

    for _branch in _remotes_branches:
        print("   ... prepare local branch from remote:", _branch)
        git_switch_branch(_repository_dir, _branch)
        git_reset_hard(_repository_dir, _branch)

    git_remote_set_url_origin(_repository_dir, _repo["to"])
    for _branch in _remotes_branches:
        print("   ... pushing to mirror branch:", _branch)
        git_switch_branch(_repository_dir, _branch)
        git_push_force(_repository_dir, _branch)
        # git push --set-upstream origin r11
    git_push_origin_tags(_repository_dir)

    print(" -> Done with", _repoid)
    os.chdir(CURRENT_DIR)
