# git-mirror-repositories

Mirroring of git-repositories

Basicly develop for mirroring repositories from github to gitlab... (backups)

## Installing

Ubuntu 24.04:
```
$ sudo apt install git
$ python3 -m pip install --break-system-packages pyyaml
$ git clone https://github.com/sea5kg/git-mirror-repositories /opt/git-mirror-repositories
$ sudo ln -s /opt/git-mirror-repositories/run_mirroring.py /usr/bin/run_mirroring
```


## Configure and run

craete direcotry `~/mirroring`

`~/mirroring/config.yml`:
```
working_directory: "./repos"

repositories:
    example:
        enabled: false
        from: "https://github.com/sea5kg/pipeline-editor-s5"
        to: "http://user:some@another.server/mirror/sea5kg/pipeline-editor-s5"
```
also you can create close another fiels with config repos, like:

`~/mirroring/config_github_sea5kg.yml` with content:
```

# repositories from https://github.com/sea5kg/

repositories:
    pipeline_editor_s5:
        enabled: true
        from: "https://github.com/sea5kg/pipeline-editor-s5"
        to: "http://user:some@another.server/mirror/sea-kg/pipeline-editor-s5.git"
```

*Note: repository http://another.server/mirror/sea5kg/pipeline-editor-s5 must exists and allow force push for user*

now you can try run:

```
$ cd ~/mirroring
$ run_mirroring
```
