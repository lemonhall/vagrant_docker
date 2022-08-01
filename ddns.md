
### DNS注册
https://docker-py.readthedocs.io/en/stable/

mkdir ~/.venvs
mkdir ~/.venvs/docker

python3 -m venv ~/.venvs/docker
source ~/.venvs/docker/bin/activate

pip install subnet-utils

#!/root/.venvs/docker/bin/python

本来我是想着，在每个容器里搞一个注册的东西，但后来转念一想，为什么不干脆自动注册好得了

### 到root用户去
sudo su

### 安装依赖

pip install docker

### Hello World 一下


	import docker
	client = docker.from_env()
	cons = client.containers.list()
	print(cons)

打印出所有的容器

import docker
client = docker.from_env()
cons = client.containers.list()
for c in cons:
    print(c.name)
    print(c.status)
    print(c.attrs['NetworkSettings']['GlobalIPv6Address'])

于是，我们最想要的三个东西都有了，容器名称，容器状态，以及，容器的ipv6的地址




{
     'Id': '770c9e78a2d95f707b6fadc1125f37c7b6259b35ac103929ce6350e0f346b6cd',
     'Created': '2022-07-30T06:08:53.921373958Z',
     'Path': '/portainer',
     'Args': [],
     'State': {
        'Status': 'running',
         'Running': True,
         'Paused': False,
         'Restarting': False,
         'OOMKilled': False,
         'Dead': False,
         'Pid': 14564,
         'ExitCode': 0,
         'Error': '',
         'StartedAt': '2022-07-31T11:41:02.472399946Z',
         'FinishedAt': '2022-07-31T11:41:01.49751896Z'
      },
     'Image': 'sha256:ab836adaa3259607fa2635fde4fbc8ed7e487ee07e316bcb20776bae363d8c98',
     'ResolvConfPath': '/var/lib/docker/containers/770c9e78a2d95f707b6fadc1125f37c7b6259b35ac103929ce6350e0f346b6cd/resolv.conf',
     'HostnamePath': '/var/lib/docker/containers/770c9e78a2d95f707b6fadc1125f37c7b6259b35ac103929ce6350e0f346b6cd/hostname',
     'HostsPath': '/var/lib/docker/containers/770c9e78a2d95f707b6fadc1125f37c7b6259b35ac103929ce6350e0f346b6cd/hosts',
     'LogPath': '/var/lib/docker/containers/770c9e78a2d95f707b6fadc1125f37c7b6259b35ac103929ce6350e0f346b6cd/770c9e78a2d95f707b6fadc1125f37c7b6259b35ac103929ce6350e0f346b6cd-json.log',
     'Name': '/portainer',
     'RestartCount': 0,
     'Driver': 'btrfs',
     'Platform': 'linux',
     'MountLabel': '',
     'ProcessLabel': '',
     'AppArmorProfile': '',
     'ExecIDs': None,
     'HostConfig': {},
     'GraphDriver': {
        'Data': None,
         'Name': 'btrfs'
    	},
     'Mounts': [],
     'Config': {},
     'NetworkSettings': {
         'Bridge': '',
         'SandboxID': '5d529412de52395a60ced86e7aa69fd79e6a4cac3c512049adb28176fd675adb',
         'HairpinMode': False,
         'LinkLocalIPv6Address': '',
         'LinkLocalIPv6PrefixLen': 0,
         'Ports': {},
         'SandboxKey': '/var/run/docker/netns/5d529412de52',
         'SecondaryIPAddresses': None,
         'SecondaryIPv6Addresses': None,
         'EndpointID': 'db10490de0a6c3376fa06ceddfee97c2586aefb218c363af135ca5792512c15b',
         'Gateway': '172.16.200.1',
         'GlobalIPv6Address': '240e:3b4:303c:d970:1000:242:ac10:c802',
         'GlobalIPv6PrefixLen': 68,
         'IPAddress': '172.16.200.2',
         'IPPrefixLen': 24,
         'IPv6Gateway': '240e:3b4:303c:d970:1000::1',
         'MacAddress': '02:42:ac:10:c8:02',
         'Networks': {
            'bridge': {
                'IPAMConfig': None,
                 'Links': None,
                 'Aliases': None,
                 'NetworkID': 'e45b6a8f1f80145d5788caccc91e70f43281f099eea24073dfac25f8700bbc05',
                 'EndpointID': 'db10490de0a6c3376fa06ceddfee97c2586aefb218c363af135ca5792512c15b',
                 'Gateway': '172.16.200.1',
                 'IPAddress': '172.16.200.2',
                 'IPPrefixLen': 24,
                 'IPv6Gateway': '240e:3b4:303c:d970:1000::1',
                 'GlobalIPv6Address': '240e:3b4:303c:d970:1000:242:ac10:c802',
                 'GlobalIPv6PrefixLen': 68,
                 'MacAddress': '02:42:ac:10:c8:02',
                 'DriverOpts': None
            }
        }
    }
}

https://techoverflow.net/2022/04/02/python-cloudflare-dns-a-record-create-or-update-example/


### 安装依赖
pip install CloudFlare


#!/usr/bin/env python3
import CloudFlare
import sys

hostname = "docker.lemonhall.me"
ipv6_address= "240e:3b4:303c:d970:1000:242:ac10:c802"

# Initialize Cloudflare API client
cf = CloudFlare.CloudFlare(
	email="lemonhall2012@qq.com",
	token="xxxxxxxxxxxxxxxxxxxxxxxx"
)
# Get zone ID (for the domain). This is why we need the API key and the domain API token won't be sufficient
zone = ".".join(hostname.split(".")[-2:]) # domain = test.mydomain.com => zone = mydomain.com
zones = cf.zones.get(params={"name": zone})
if len(zones) == 0:
	print(f"Could not find CloudFlare zone {zone}, please check domain {hostname}")
	sys.exit(2)

zone_id = zones[0]["id"]

# Fetch existing A record
aaaa_records = cf.zones.dns_records.get(zone_id, params={"name": hostname, "type": "AAAA"})

if len(aaaa_records): # Have an existing record
    print("Found existing record, updating...")
    a_record = aaaa_records[0]
    # Update record & save to cloudflare
    a_record["content"] = ipv6_address
    cf.zones.dns_records.put(zone_id, a_record["id"], data=a_record)
else: # No existing record. Create !
    print("Record doesn't existing, creating new record...")
    a_record = {}
    a_record["type"] = "AAAA"
    a_record["name"] = hostname
    a_record["ttl"] = 60 # 1 == auto
    a_record["content"] = ipv6_address
    cf.zones.dns_records.post(zone_id, data=a_record)



 # 10 # DSM Config3
 # 11 username="80fb982431acc54b5fa87f5811e5bf7a" #zoneid
 # 12 password="c0b4ccf61bfd1e222adb18259b39e02516a08" #apikey
 # 13 hostname="lemonhall.me" #hostname

 /root/docker_ddns/ddns.py
 



