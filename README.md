# Pilot

Simple web-based SDN controller for family and friends.

[![Build Status](https://dev.azure.com/nekomimiswitch/General/_apis/build/status/pilot?branchName=master)](https://dev.azure.com/nekomimiswitch/General/_build/latest?definitionId=81&branchName=master)

## Introduction

Pilot acts as a frontend for GoBGP, which allows any device in your LAN to open a web page and select their own network profile based on pre-defined route targets.

![](assets/pilot-webui.png)

## Requirements

Server running Pilot:
* Python 3.7 or later
* LAN devices should not go through SNAT/masquerade to access the server

Router (network gateway):
* Has VRF-Lite capability
* Supports [BGP Flow Specification](https://tools.ietf.org/html/rfc5575) client

## Usage

### Router Setup

* Put different network profiles are put in different VRFs
* Add BGP session with your GoBGP instance and enable `ipv4 flowspec` and `ipv6 flowspec` address families
* Allow flowspec rule installation on the interfaces to LAN clients

### Pilot Setup

Download all the files in [config](config) and put them in a directory. 

In `gobgpd.toml`:
* Change `global.config.as` and `global.config.router-id`
* Change `neighbors[].config.neighbor-address` and `neighbors[].config.peer-as`

In `pilot.toml`:
* Add or change `rule`

Then spin up our Docker container:
```shell script
docker run --restart=always --name=pilot -p 80:80 -v path/to/your/config/directory:/etc/pilot:ro jamesits/pilot:latest
```

The web UI will be on port 80.

## Thanks

This project is inspired by [xtomcom/NetworkSwitch](https://github.com/xtomcom/NetworkSwitch).

