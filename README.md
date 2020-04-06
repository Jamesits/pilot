# Pilot

Simple web-based SDN controller for family and friends.

[![Build Status](https://dev.azure.com/nekomimiswitch/General/_apis/build/status/pilot?branchName=master)](https://dev.azure.com/nekomimiswitch/General/_build/latest?definitionId=81&branchName=master)

## Introduction

Pilot is a frontend of GoBGP. Any device in your LAN can visit Pilot's web interface to easily select their own VRF.

![Pilot web interface screenshot](assets/pilot-webui.png)

## Requirements

Server running Pilot:
* Python 3.7 or later
* LAN devices should not go through SNAT/masquerade to access the server

Gateway router:
* Has VRF-Lite capability
* Can act as a [BGP Flow Specification](https://tools.ietf.org/html/rfc5575) client

## Usage

### Router Setup

* Put different network profiles in different VRFs
* Add BGP session with your GoBGP instance and enable `ipv4 flowspec` and `ipv6 flowspec` address families
* Allow flowspec rule installation on the interfaces to LAN clients

Example configuration for Cisco IOS XE 16.x:
```
! enable flowspec rule installation
flowspec
 local-install interface-all

! VRF definition
ip vrf UPLINK1
 rd 100:100
 route-target both 100:100
ip vrf UPLINK2
 rd 200:200
 route-target both 200:200

! Uplink interfaces
interface GigabitEthernet0/0/0
 description uplink-1
 ip vrf select source
 ip vrf receive UPLINK1
 ip flowspec disable
interface GigabitEthernet0/0/1
 description uplink-2
 ip vrf select source
 ip vrf receive UPLINK2
 ip flowspec disable

! LAN interfaces
interface GigabitEthernet0/0/2
 description LAN
 ip address 192.168.1.1 255.255.255.0
 ip vrf select source
 ip vrf receive UPLINK1
 ip vrf receive UPLINK2

! BGP peer setup
router bgp 65540
 bgp router-id 169.254.1.2
 neighbor 169.254.1.1 remote-as 65540
 address-family ipv4 flowspec
  neighbor 169.254.1.1 activate
  neighbor 169.254.1.1 soft-reconfiguration inbound
 address-family ipv6 flowspec
  neighbor 169.254.1.1 activate
  neighbor 169.254.1.1 soft-reconfiguration inbound

! Routes for global and VRFs
ip route 0.0.0.0 0.0.0.0 x.x.x.x 10
ip route 0.0.0.0 0.0.0.0 y.y.y.y 20
ip route vrf UPLINK1 0.0.0.0 0.0.0.0 x.x.x.x
ip route vrf UPLINK2 0.0.0.0 0.0.0.0 y.y.y.y
```

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

