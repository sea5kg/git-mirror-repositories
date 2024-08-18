#!/usr/bin/env python3
# Copyright (c) 2024 Evgenii Sopov <mrseakg@gmail.com>

import os
import sys
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

if 'repositories' not in CONFIG:
    sys.exit("Not found 'repositories' in " + CONFIG_PATH_YML)

for _repoid in CONFIG["repositories"]:
    print("Start mirorring... ",_repoid)

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

    # todo get list of branches and tags - remember

    print("Done with", _repoid)
    os.chdir(CURRENT_DIR)

