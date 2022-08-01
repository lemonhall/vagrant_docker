#!/root/.venvs/docker/bin/python

import os
from subnet import ip_network, IPv4Network, IPv6Network
import json
import fileinput
import docker
import CloudFlare
import sys
from time import sleep

# Initialize Cloudflare API client
#token是你的api_key
cf = CloudFlare.CloudFlare(
    email="lemonhall2012@qq.com",
    token="xxxxxxxxxxxxxxxxxxxxxxxxx"
)

#更新ipv6地址的函数
#hostname="docker.lemonhall.me"
#ipv6_address=""
def dns_updater(hostname,ipv6_address):
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

#计算系统当前的ipv6地址对应的第二个子网的前缀【这个东西需要提升到全局变量去】，另外网卡名称也需要
#240e:3b4:303c:9790:1000::/68
def now_prefix():
    print("====I am in now_prefix=====")
    ipv6=""
    try:
        #我是在用crontab调度这个脚本，这个脚本在crontab下得给出全名，这个必须在移植到别的系统时，小心这个事情
        ipv6 = os.popen("/usr/sbin/ip addr show wlp3s0 | /usr/bin/grep '\<inet6\>' | /usr/bin/head -n1 | /usr/bin/awk '{ print $2 }' | /usr/bin/awk -F '/' '{ print $1 }'").read().strip()
    except Exception as e:
        print(e)
    print("the ipv6 is")
    print(ipv6)
    print("end of get ipv6....what??? empty?")

    ip_parts = ipv6.split(":")
    new_ipv6 = ip_parts[0]+":"+ip_parts[1]+":"+ip_parts[2]+":"+ip_parts[3]+"::"+"/64"
    my_ipv6_subnet = IPv6Network(new_ipv6)
    n=0
    my_subnet = ""
    for subnet in my_ipv6_subnet.divide(16):
        if n==1:
            my_subnet=subnet
        n=n+1
    return my_subnet
# 写入老文件
def write_to_old_prefix_buffer(content):
    with open("old_prefix_buffer.txt","w",encoding='utf8') as f:
        f.write(content)
        f.close
#读取老文件
def read_old_prefix_buffer():
    old_prefix_buffer=""
    with open("old_prefix_buffer.txt",encoding='utf8') as f:
        old_prefix_buffer = f.read()
        f.close
    return old_prefix_buffer
#判断是否有变化
def if_diff(now_prefix):
    old_prefix_buffer = read_old_prefix_buffer()
    if old_prefix_buffer == now_prefix:
        print("same")
        return True
    else:
        print("not same")
        print("now_prefix:"+now_prefix)
        print("old_prefix:"+old_prefix_buffer)
        write_to_old_prefix_buffer(now_prefix)
        return False
#写docker的配置文件，修改fixed-cidr-v6这一个项目
def write_to_daemon_json(prefix):
    f = open('/etc/docker/daemon.json',encoding='utf8')
    data = json.load(f)
    f.close
    data['fixed-cidr-v6']=prefix
    print(data)
    json_string = json.dumps(data)
    # Directly from dictionary
    with open('/etc/docker/daemon.json','w',encoding='utf8') as outfile:
        outfile.write(json_string)
        outfile.close
#替换ndpp.conf文件的内容，将rule这一行替换成新的网段地址
def replace_ndppd(prefix):
    filename = "/etc/ndppd.conf"
    with fileinput.FileInput(filename, inplace = True, backup ='.bak') as f:
        for line in f:
            if("   rule" in line):
                print("   rule "+prefix+"  {", end ='\n')
            else:
                print(line, end='')

print("====main begin====")
#主程序开始
prefix=str(now_prefix())
print("====prefix getd===")
print(prefix)

with open("py.log","w",encoding='utf8') as log:
    log.write("I am in main\n")
    log.write("prefix:   "+prefix+"\n")
    if if_diff(prefix):
        pass
    else:
        print("打开/etc/docker/daemon.json文件，修改里面的fixed-cidr-v6值为prefix")
        write_to_daemon_json(prefix)
        print("重启docker")
        os.system("systemctl restart docker")
        print("sleeping 5 secs")
        sleep(5)
        replace_ndppd(prefix)
        print("重启ndppd")
        os.system("systemctl restart ndppd")
        os.system("curl https://lemonhall.synology.me:25050/push?content='ipv6重启了docker'")
        print("sleeping 5 secs")
        sleep(5)
        ####更新dns的AAAA记录的过程开始
        ####更新dns的AAAA记录的过程开始
        client = docker.from_env()
        cons = client.containers.list()
        for c in cons:
            if(c.status=="running"):
                print(c.name)
                print(c.status)
                print(c.attrs['NetworkSettings']['GlobalIPv6Address'])
                hostname     = c.name+".lemonhall.me"
                ipv6_address = c.attrs['NetworkSettings']['GlobalIPv6Address']
                dns_updater(hostname,ipv6_address)
                print("sleeping 2 secs")
                sleep(2)
                os.system("curl https://lemonhall.synology.me:25050/push?content='"+hostname+"可用了'")
    log.close()