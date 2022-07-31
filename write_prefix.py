import os
from subnet import ip_network, IPv4Network, IPv6Network
import json

#计算系统当前的ipv6地址对应的第二个子网的前缀
#240e:3b4:303c:9790:1000::/68
def now_prefix():
    ipv6 = os.popen('ip addr show wlp3s0 | grep "\<inet6\>" | head -n1 | awk \'{ print $2 }\' | awk -F "/" \'{ print $1 }\'').read().strip()
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
        write_to_old_prefix_buffer(now_prefix)
        return False
#写配置文件
def write_to_daemon_json(prefix):
    f = open('/etc/docker/daemon.json',encoding='utf8')
    data = json.load(f)
    f.close
    data['fixed-cidr-v6']=prefix
    json_string = json.dumps(data)
    # Directly from dictionary
    with open('/etc/docker/daemon.json','w',encoding='utf8') as outfile:
        outfile.write(json_string)
        outfile.close

#主程序开始
prefix=str(now_prefix())
if if_diff(prefix):
    pass
else:
    print("打开/etc/docker/daemon.json文件，修改里面的fixed-cidr-v6值为prefix")
    write_to_daemon_json(prefix)
    print("重启docker")
    os.system("systemctl restart docker")