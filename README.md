# Beepy Network Manager

## Overview

This is a Beepy app to manage WiFi networks. The application is written in Python, using [Textual](https://textual.textualize.io/) for the TUI. You should install this through the [bapp-store](https://github.com/conor-f/bapp-store), but if you want to run this on a non-Beepy device, the `justfile` gives a pretty clear indication of what to do (or look at the Developer Quickstart below). In addition to the TUI, you can use `beepy_network_manager` as a regular CLI.

[Demo GIF placeholder - Update with new demo when available]

```
$ beepy_network_manager --help
usage: beepy_network_manager [-h] {list,connect,disconnect,status} ...

Beepy Network Manager CLI

positional arguments:
  {list,connect,disconnect,status}  Available commands
    list                            List available WiFi networks
    connect                         Connect to a WiFi network
    disconnect                      Disconnect from the current network
    status                          Check current network status

options:
  -h, --help                        show this help message and exit
```

## Developer Quickstart

```
$ just init
$ just run
$ just run --help
```

The `just init` rule will install a number of pre-commit hooks in addition to installing the actual project.


## TODO
- [ ] Provide better error messages
