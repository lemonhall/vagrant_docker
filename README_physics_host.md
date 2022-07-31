环境
====
* fedora36
* 5.18的内核
* docker官方版本

目的
====
将物理机器上的容器子网直接暴露在局域网内，不再做麻烦的port forwarding

<img width="1160" alt="image" src="https://user-images.githubusercontent.com/637919/181862526-44b3c370-b190-4b3e-abb7-93d943936432.png">

配置裸机器的docker
==================
给docker一个不同的子网段

* sudo vim /etc/docker/daemon.json

  {
    "bip": "172.16.200.1/24"
  }

重启服务
=======
物理机上重启

sudo systemctl restart docker

配置路由
========

到物理路由器里面去，华硕的，UI上加上静态路由规则

配置一条
172.16.200.0 mask 255.255.255.0 gw 192.168.50.12 
的路由规则

修改物理机防火墙
================

然后直接干掉防火墙
* sudo systemctl disable --now firewalld

然后我看了FORWARD默认是drop，所有需要全部ACCEPT

* sudo iptables -P FORWARD ACCEPT

测试
====

从别的机器ping

	lemon@LEMON-HP-LAPTOP:~$ ping 172.16.200.2
	PING 172.16.200.2 (172.16.200.2) 56(84) bytes of data.
	64 bytes from 172.16.200.2: icmp_seq=1 ttl=62 time=18.5 ms
	64 bytes from 172.16.200.2: icmp_seq=2 ttl=62 time=18.7 ms
	64 bytes from 172.16.200.2: icmp_seq=3 ttl=62 time=22.3 ms
	64 bytes from 172.16.200.2: icmp_seq=4 ttl=62 time=18.7 ms
	64 bytes from 172.16.200.2: icmp_seq=5 ttl=62 time=18.5 ms
	64 bytes from 172.16.200.2: icmp_seq=6 ttl=62 time=18.7 ms
	64 bytes from 172.16.200.2: icmp_seq=7 ttl=62 time=18.8 ms
	64 bytes from 172.16.200.2: icmp_seq=8 ttl=62 time=21.3 ms
	^C
	--- 172.16.200.2 ping statistics ---
	8 packets transmitted, 8 received, 0% packet loss, time 7013ms
	rtt min/avg/max/mdev = 18.487/19.430/22.297/1.388 ms
	lemon@LEMON-HP-LAPTOP:~$

成功，很好，再试试别的

临时run一个xdp的例子

sudo docker run -it --rm --privileged lemonhall/xdp_demo bash

大概1.1G左右

哦吼，这个例子的拉取是需要密码的
所有需要

sudo docker login

先
然后运行

之后ping 200.3也是ok的

在3号容器里，ping www.baidu.com
也是ok的

容器里，ping 192.168.50.46
其它的物理机器，都是通畅的，自此，裸机配置完毕

![image](https://user-images.githubusercontent.com/637919/181918956-b6a28238-9079-4656-a168-16c70da3d523.png)

https://172.16.200.2:9443/

jH2U6s7s!^ZcYW7R

告别端口转发的痛苦

搞ipv6才是正经事啊
================

物理机上

	sudo ip -6 addr show dev wlp3s0

	2: wlp3s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
	    inet6 240e:3b4:303b:5830:d176:3e26:24e:1de0/64 scope global dynamic noprefixroute
	       valid_lft 597sec preferred_lft 597sec
	    inet6 fe80::f2f9:df78:1b5c:a6ea/64 scope link noprefixroute
	       valid_lft forever preferred_lft forever


	sudo ip -6 route show

	::1 dev lo proto kernel metric 256 pref medium
	240e:3b4:303b:5830::/64 dev wlp3s0 proto ra metric 600 pref medium
	fe80::/64 dev docker0 proto kernel metric 256 pref medium
	fe80::/64 dev veth4f2db83 proto kernel metric 256 pref medium
	fe80::/64 dev wlp3s0 proto kernel metric 1024 pref medium
	default via fe80::b26e:bfff:fe28:92c0 dev wlp3s0 proto ra metric 600 pref medium


link-local address, 中文叫“链路本地地址”，它的前缀是
FE80::/64
一个link-local address的范例：
FE80::713e:a426:d167:37ab

实际上，这个概念类似于ipv4中，当DHCP分配失败时自动生成的169.254.XXX.XXX这样的地址，凡是源地址或目的地址中含有link-local address的报文，路由器都不应当转发它。这样的报文只能在一个LAN中互通。

[How to enable IPv6 for Docker containers on Ubuntu 18.04]
(https://medium.com/@skleeschulte/how-to-enable-ipv6-for-docker-containers-on-ubuntu-18-04-c68394a219a2)

ip addr show $(ip -6 route show | awk '/^default/ {print $5}') | awk '/inet6 .* scope global/ {print $2}'

* sudo vim /etc/docker/daemon.json

"ipv6": true

物理机上重启

sudo systemctl restart docker

failed to start daemon: Error initializing network controller: IPv6 is enabled for the default bridge, but no subnet is configured. Specify an IPv6 subnet

报错，失败

	sudo nmcli device show

	GENERAL.DEVICE:                         wlp3s0
	GENERAL.TYPE:                           wifi
	GENERAL.HWADDR:                         34:36:3B:CD:FC:18
	GENERAL.MTU:                            1500
	GENERAL.STATE:                          100（已连接）
	GENERAL.CONNECTION:                     lemon_5g_Gaming
	GENERAL.CON-PATH:                       /org/freedesktop/NetworkManager/ActiveConnection/6
	IP4.ADDRESS[1]:                         192.168.50.12/24
	IP4.GATEWAY:                            192.168.50.1
	IP4.ROUTE[1]:                           dst = 192.168.50.0/24, nh = 0.0.0.0, mt = 600
	IP4.ROUTE[2]:                           dst = 0.0.0.0/0, nh = 192.168.50.1, mt = 600
	IP4.DNS[1]:                             192.168.50.1
	IP6.ADDRESS[1]:                         240e:3b4:303b:5830:d176:3e26:24e:1de0/64
	IP6.ADDRESS[2]:                         fe80::f2f9:df78:1b5c:a6ea/64
	IP6.GATEWAY:                            fe80::b26e:bfff:fe28:92c0
	IP6.ROUTE[1]:                           dst = fe80::/64, nh = ::, mt = 1024
	IP6.ROUTE[2]:                           dst = 240e:3b4:303b:5830::/64, nh = ::, mt = 600
	IP6.ROUTE[3]:                           dst = ::/0, nh = fe80::b26e:bfff:fe28:92c0, mt = 600
	IP6.DNS[1]:                             240e:3b4:303b:5830::1

	GENERAL.DEVICE:                         docker0
	GENERAL.TYPE:                           bridge
	GENERAL.HWADDR:                         02:42:44:A2:4E:43
	GENERAL.MTU:                            1500
	GENERAL.STATE:                          100（连接（外部））
	GENERAL.CONNECTION:                     docker0
	GENERAL.CON-PATH:                       /org/freedesktop/NetworkManager/ActiveConnection/2
	IP4.ADDRESS[1]:                         172.16.200.1/24
	IP4.GATEWAY:                            --
	IP4.ROUTE[1]:                           dst = 172.16.200.0/24, nh = 0.0.0.0, mt = 0
	IP6.ADDRESS[1]:                         fe80::42:44ff:fea2:4e43/64
	IP6.GATEWAY:                            --
	IP6.ROUTE[1]:                           dst = fe80::/64, nh = ::, mt = 256

	GENERAL.DEVICE:                         DC:33:3D:22:F2:B3
	GENERAL.TYPE:                           bt
	GENERAL.HWADDR:                         DC:33:3D:22:F2:B3
	GENERAL.MTU:                            0
	GENERAL.STATE:                          30（已断开）
	GENERAL.CONNECTION:                     --
	GENERAL.CON-PATH:                       --

	GENERAL.DEVICE:                         lo
	GENERAL.TYPE:                           loopback
	GENERAL.HWADDR:                         00:00:00:00:00:00
	GENERAL.MTU:                            65536
	GENERAL.STATE:                          10（未托管）
	GENERAL.CONNECTION:                     --
	GENERAL.CON-PATH:                       --
	IP4.ADDRESS[1]:                         127.0.0.1/8
	IP4.GATEWAY:                            --
	IP6.ADDRESS[1]:                         ::1/128
	IP6.GATEWAY:                            --
	IP6.ROUTE[1]:                           dst = ::1/128, nh = ::, mt = 256

使用关键词搜索：docker ipv6 DHCP-PD

	https://github.com/wido/docker-ipv6

You need to make a script that requests a prefix from your router. This is done over DHCPv6.

This is required for your router to properly setup its routing table, so it routes the traffic back.

The design of docker requires that you restart all containers when the prefix used for the containers changes



	sudo dnf install dhcp-client

这个脚本其实还依赖一个命令叫做sipcalc，应该就是计算子网的

	sudo dnf install sipcalc

https://github.com/wido/docker-ipv6/blob/master/docker-ipv6

SUBNET=$(sipcalc -S $SUBNET_SIZE $new_ip6_prefix|grep Network|head -n 1|awk '{print $3}')

sipcalc -S 80 

dhclient -6 -P -d wlp3s0

dhclient6-pd.service

	[Unit]
	Description=DHCPv6 Prefix Delegation client
	Wants=network.target network-online.target
	After=network.target network-online.target

	[Service]
	Type=simple
	Environment=NETWORK_INTERFACE=wlp3s0
	ExecStart=/sbin/dhclient -6 -P -d ${NETWORK_INTERFACE}
	Restart=always
	RestartSec=10s

	[Install]
	WantedBy=multi-user.target

cd /etc/systemd/system/
sudo vim dhclient6-pd.service

sudo systemctl daemon-reload
sudo systemctl start dhclient6-pd
sudo systemctl enable dhclient6-pd

开机自启动

在/etc/default/docker文件里，写入内容

DOCKER_OPTS="--ipv6 --fixed-cidr-v6=`cat /etc/docker/ipv6.prefix`"

文件：docker-ipv6

#!/bin/bash
#
# DHCPv6 hook for Docker
#
# This hook will configure Docker to use the first /80 IPv6 subnet
# from the Prefix we got through DHCPv6 Prefix Delegation
#
# A /80 subnet is large enough for Docker. 80 + 48 bits (MAC) equals 128-bits.
#
# dhclient will run this hook after it obtains the lease
#
# Make sure you can dhclient in a way that it requests a prefix, eg:
#
# dhclient -6 -P -d eth0
#
# With the new prefix we can reconfigure Docker and restart it
#
# Make sure /etc/default/docker contains:
#
# DOCKER_OPTS="--ipv6 --fixed-cidr-v6=`cat /etc/docker/ipv6.prefix`"
#
# This script requires sipcalc to function
command -v sipcalc >/dev/null 2>&1 || exit 0

SUBNET_SIZE=80
DOCKER_ETC_DIR="/etc/docker"
DOCKER_PREFIX_FILE="${DOCKER_ETC_DIR}/ipv6.prefix"

if [ ! -z "$new_ip6_prefix" ]; then
    SUBNET=$(sipcalc -S $SUBNET_SIZE $new_ip6_prefix|grep Network|head -n 1|awk '{print $3}')
    echo "${SUBNET}/${SUBNET_SIZE}" > $DOCKER_PREFIX_FILE

    if [ "$old_ip6_prefix" != "$new_ip6_prefix" ]; then
        service docker restart
    fi
fi

新建了文件夹:
sudo mkdir /etc/dhcp/dhclient-enter-hooks.d/


	ls 某abc文件夹需要文件夹有r权限。

	cd  某abc文件夹 需要文件夹有x权限。

	chmod a+x abc

	chmod a+r abc

http://www.gestioip.net/cgi-bin/subnet_calculator.cgi

我的路由器告诉我：

我的：LAN IPv6 Prefix:
240e:3b4:303b:5830::/60

然后计算器告诉我：
IP address	240e:3b4:303b:5830::/60
type	GLOBAL-UNICAST
network	240e:3b4:303b:5830::
Prefix length	60
network range	240e:03b4:303b:5830:0000:0000:0000:0000-
240e:03b4:303b:583f:ffff:ffff:ffff:ffff
total IP addresses	295147905179352825856

我的ip地址可以，240e:03b4:303b:5830===>240e:03b4:303b:583f
我的天啊，这么多么

### 然后是这台物理机器
https://blog.csdn.net/easylife206/article/details/119550357

这么开其实是有意义，也没意义，没意义的地方在于。。。

机器确实是得到了ipv6地址，但是路由信息却没有进入路由器

240e:3b4:303b:5830:d176:3e26:24e:1de0

IP address	240e:3b4:303b:5830:d176:3e26:24e:1de0/64
type	GLOBAL-UNICAST
network	240e:3b4:303b:5830::
Prefix length	64
network range	240e:03b4:303b:5830:0000:0000:0000:0000-
240e:03b4:303b:5830:ffff:ffff:ffff:ffff
total IP addresses	18446744073709551616

240e:03b4:303b:5830:0000::/68
240e:03b4:303b:5830:1000::/68
240e:03b4:303b:5830:2000::/68
240e:03b4:303b:5830:3000::/68
240e:03b4:303b:5830:4000::/68
240e:03b4:303b:5830:5000::/68
240e:03b4:303b:5830:6000::/68
240e:03b4:303b:5830:7000::/68
240e:03b4:303b:5830:8000::/68
240e:03b4:303b:5830:9000::/68
240e:03b4:303b:5830:a000::/68
240e:03b4:303b:5830:b000::/68
240e:03b4:303b:5830:c000::/68
240e:03b4:303b:5830:d000::/68
240e:03b4:303b:5830:e000::/68
240e:03b4:303b:5830:f000::/68

https://www.snbforums.com/threads/asus-routers-and-ipv6-static-routes.55827/


Is there any way to define static routes for IPv6 addresses end scopes/prefixes on Asus routers? I'm currently running Asus Merlin 384.10 on a Asus RT-AX88U and I have a Palo Alto VM-300 series firewall running IP-Sec Site-to-Site VPN tunnels and currently I have to set manual routes on all my clients in order for routing traffic that is supposed to use the IP-Sec tunnel to actually hit my Palo Alto Firewall instead of just using the default gateway and be routed over the Internet.

I had the exact same setup previously, but on IPv4 and then I just went to LAN-settings on my RT-AX88U and defined a static route for 172.30.2.0/24 to be routed to 172.30.66.111 which was the Palo Alto interface in the same subnet.

The page for static routes in the WebUI does not let me set routes for IPv6 so I can't replicate this behaviour in the WebUI. Otherwise it would be as simple as telling that the remote IPv6 Prefix is behind the IPv6 address of my Palo Alto Firewall.

Is it possible to achieve this through SSH or am I forced into doing manual routes on each client?


答案就是，用ssh

You can via ssh. I know this is a very late response. I do not know how at this time to make them "permanent". I've listed an example below. The route is cleared once the router is reloaded though. I have not found a way to make it stay. I came here looking for an answer to that when I found your question.

route -A inet6 add 240e:03b4:303b:5830:1000::/68 gw 240e:3b4:303b:5830:d176:3e26:24e:1de0 dev br0
=================

https://irq5.io/2018/12/28/extending-asuswrt-functionality-part-2/

然后可以用USB来记录配置，这个倒是简单

现在的问题是，和ipv4不同

我添加了这条路由信息之后，外网确实是可以访问我的docker内部容器了，确实也正确路由了

但仅限于internal===>router===>docker0===>container2，这条链路

内网的其它机器却访问不了这台机器，非常奇怪


cat /proc/sys/net/ipv6/conf/all/forwarding
cat /proc/sys/net/ipv6/conf/wlp3s0/accept_ra

echo 1 > /proc/sys/net/ipv6/conf/wlp3s0/accept_ra


	[lemonhall@fedora36-macbook ~]$ sudo ip6tables -L
	Chain INPUT (policy ACCEPT)
	target     prot opt source               destination

	Chain FORWARD (policy ACCEPT)
	target     prot opt source               destination

	Chain OUTPUT (policy ACCEPT)
	target     prot opt source               destination
	[lemonhall@fedora36-macbook ~]$


 sudo tcpdump -n -i any icmp6

 ping6的包需要这样监听

 在另一台机器上ping它
 ping6 240e:3b4:303b:5830:d176:3e26:24e:1de0

 好，然后再试试ping docker里面的东西

 https://www.ipaddressguide.com/ping6

 240e:3b4:303b:5830:1000:242:ac10:c802

 用网页ping 容器

	 09:20:20.053852 wlp3s0 In  IP6 2a03:b0c0:3:d0::101:4001 > 240e:3b4:303b:5830:1000:242:ac10:c802: ICMP6, echo request, id 62670, seq 1, length 64
	09:20:20.053892 docker0 Out IP6 2a03:b0c0:3:d0::101:4001 > 240e:3b4:303b:5830:1000:242:ac10:c802: ICMP6, echo request, id 62670, seq 1, length 64
	09:20:20.053904 veth8da0166 Out IP6 2a03:b0c0:3:d0::101:4001 > 240e:3b4:303b:5830:1000:242:ac10:c802: ICMP6, echo request, id 62670, seq 1, length 64
	09:20:20.053939 veth8da0166 P   IP6 240e:3b4:303b:5830:1000:242:ac10:c802 > 2a03:b0c0:3:d0::101:4001: ICMP6, echo reply, id 62670, seq 1, length 64
	09:20:20.053939 docker0 In  IP6 240e:3b4:303b:5830:1000:242:ac10:c802 > 2a03:b0c0:3:d0::101:4001: ICMP6, echo reply, id 62670, seq 1, length 64
	09:20:20.053964 wlp3s0 Out IP6 240e:3b4:303b:5830:1000:242:ac10:c802 > 2a03:b0c0:3:d0::101:4001: ICMP6, echo reply, id 62670, seq 1, length 64
	09:20:21.036580 wlp3s0 In  IP6 2a03:b0c0:3:d0::101:4001 > 240e:3b4:303b:5830:1000:242:ac10:c802: ICMP6, echo request, id 62670, seq 2, length 64
	09:20:21.036616 docker0 Out IP6 2a03:b0c0:3:d0::101:4001 > 240e:3b4:303b:5830:1000:242:ac10:c802: ICMP6, echo request, id 62670, seq 2, length 64
	09:20:21.036628 veth8da0166 Out IP6 2a03:b0c0:3:d0::101:4001 > 240e:3b4:303b:5830:1000:242:ac10:c802: ICMP6, echo request, id 62670, seq 2, length 64
	09:20:21.036661 veth8da0166 P   IP6 240e:3b4:303b:5830:1000:242:ac10:c802 > 2a03:b0c0:3:d0::101:4001: ICMP6, echo reply, id 62670, seq 2, length 64
	09:20:21.036661 docker0 In  IP6 240e:3b4:303b:5830:1000:242:ac10:c802 > 2a03:b0c0:3:d0::101:4001: ICMP6, echo reply, id 62670, seq 2, length 64
	09:20:21.036680 wlp3s0 Out IP6 240e:3b4:303b:5830:1000:242:ac10:c802 > 2a03:b0c0:3:d0::101:4001: ICMP6, echo reply, id 62670, seq 2, length 64
	09:20:22.037322 wlp3s0 In  IP6 2a03:b0c0:3:d0::101:4001 > 240e:3b4:303b:5830:1000:242:ac10:c802: ICMP6, echo request, id 62670, seq 3, length 64
	09:20:22.037357 docker0 Out IP6 2a03:b0c0:3:d0::101:4001 > 240e:3b4:303b:5830:1000:242:ac10:c802: ICMP6, echo request, id 62670, seq 3, length 64
	09:20:22.037369 veth8da0166 Out IP6 2a03:b0c0:3:d0::101:4001 > 240e:3b4:303b:5830:1000:242:ac10:c802: ICMP6, echo request, id 62670, seq 3, length 64
	09:20:22.037403 veth8da0166 P   IP6 240e:3b4:303b:5830:1000:242:ac10:c802 > 2a03:b0c0:3:d0::101:4001: ICMP6, echo reply, id 62670, seq 3, length 64
	09:20:22.037403 docker0 In  IP6 240e:3b4:303b:5830:1000:242:ac10:c802 > 2a03:b0c0:3:d0::101:4001: ICMP6, echo reply, id 62670, seq 3, length 64
	09:20:22.037455 wlp3s0 Out IP6 240e:3b4:303b:5830:1000:242:ac10:c802 > 2a03:b0c0:3:d0::101:4001: ICMP6, echo reply, id 62670, seq 3, length 64

看了一下，其实是通了。。。

然后我在dns上配置一下
docker.lemonhall.me points to 240e:3b4:303b:5830:1000:242:ac10:c802.

一个AAAA的记录

https://www.uptrends.com/tools/ipv6-ping-test

用这个测的，都很好，奇怪了

https://docker.lemonhall.me:9443/#!/home

外网竟然也是可以的，我用手机测了一下ok了

但是内网。。。。不行，？啊哈？

有点懵
====
外网通了，内网unreachable?????

1、外部能到说明是
只要流量到了我的macbook，我的机器就能正确处理，并转发到docker0，docker0也正确处理了，并且正确转发到容器

容器也正确返回了

sudo sysctl net.ipv6.conf.wlp3s0.accept_ra=2

cat /proc/sys/net/ipv6/conf/wlp3s0/accept_ra

Docker IPv6 networking, routing, and NDP proxying

https://blog.apnic.net/2021/07/06/docker-ipv6-networking-routing-and-ndp-proxying/

The host will now be able to route packets to the container, but other devices still won’t know that the host is responsible for the container’s address. There are a few ways to fix this depending on your exact network setup, such as having the Docker host make RAs, or adding the subnet to a router as a static route. The static route option is noteworthy for also being possible with IPv4, if desired.

https://medium.com/@skleeschulte/how-to-enable-ipv6-for-docker-containers-on-ubuntu-18-04-c68394a219a2

By enabling Docker’s IPv6 functionality, forwarding of IPv6 packets gets automatically enabled in the host’s kernel. However, the containers are still not directly reachable from the internet. The reason is that the network router cannot find out how to forward IPv6 packets to the Docker containers. To change this, the host must be configured to proxy NDP (Neighbor Discovery Protocol) messages to the containers.


sudo sysctl net.ipv6.conf.wlp3s0.proxy_ndp=1

sudo ip -6 neigh add proxy 240e:3b4:303b:5830:1000:242:ac10:c802 dev wlp3s0


PING6(56=40+8+8 bytes) 240e:3b4:303b:5830:fdab:be59:48af:4f1c --> 240e:3b4:303b:5830:1000:242:ac10:c802
16 bytes from 240e:3b4:303b:5830:1000:242:ac10:c802, icmp_seq=1028 hlim=63 time=498.866 ms
16 bytes from 240e:3b4:303b:5830:1000:242:ac10:c802, icmp_seq=1029 hlim=63 time=9.721 ms
16 bytes from 240e:3b4:303b:5830:1000:242:ac10:c802, icmp_seq=1030 hlim=63 time=9.633 ms
16 bytes from 240e:3b4:303b:5830:1000:242:ac10:c802, icmp_seq=1031 hlim=63 time=9.064 ms
16 bytes from 240e:3b4:303b:5830:1000:242:ac10:c802, icmp_seq=1032 hlim=63 time=3.153 ms

然后，局域网内部就可以了

Setting up the NDP Proxy Daemon
===============================

安装

sudo dnf search ndppd

直接到etc下

cd /etc/

把route eth0

修改成自己的dev

wlp3s0

然后修改界面：
rule 240e:03b4:303b:5830:1000::/68 


sudo systemctl enable ndppd
sudo systemctl restart ndppd

找到局域网内的另外一台物理机器：

sudo docker run -it --rm --privileged lemonhall/xdp_demo bash

新启动一个容器，并且拿它的ipv6地址看一下

	(base) lemonhall@mac-book-pro:~$ ping6 240e:3b4:303b:5830:1000:242:ac10:c803
	PING6(56=40+8+8 bytes) 240e:3b4:303b:5830:fdab:be59:48af:4f1c --> 240e:3b4:303b:5830:1000:242:ac10:c803
	16 bytes from 240e:3b4:303b:5830:1000:242:ac10:c803, icmp_seq=0 hlim=63 time=343.357 ms
	16 bytes from 240e:3b4:303b:5830:1000:242:ac10:c803, icmp_seq=1 hlim=63 time=2.227 ms
	16 bytes from 240e:3b4:303b:5830:1000:242:ac10:c803, icmp_seq=2 hlim=63 time=9.679 ms
	^C
	--- 240e:3b4:303b:5830:1000:242:ac10:c803 ping6 statistics ---
	3 packets transmitted, 3 packets received, 0.0% packet loss
	round-trip min/avg/max/std-dev = 2.227/118.421/343.357/159.083 ms
	(base) lemonhall@mac-book-pro:~$


ok，ping成功了

再测试之前的地址

https://docker.lemonhall.me:9443/#!/home

不行

找到系统代理服务设置

把
* [*.lemonhall.me配置进去，不要走默认的代理服务，oh，yeah，成功咯]


问题
===

1、这个东西过于动态化了，很烦人

2、我重启了路由器，你看，刚才写得那条静态路由就没有用了
route -A inet6 add 240e:03b4:303b:5830:1000::/68 gw 240e:3b4:303b:5830:d176:3e26:24e:1de0 dev br0

因为，物理机的ipv6地址彻底变了

新地址是
240e:3b4:303c:9790:18fe:fda0:9fcf:271c/64

http://www.gestioip.net/cgi-bin/subnet_calculator.cgi

我使用它来计算一下

切成16个子网

240e:03b4:303c:9790:1000::/68

我选了第一个

更新docker的配置

sudo vim /etc/docker/daemon.json

重启

sudo systemctl restart docker

jH2U6s7s!^ZcYW7R

容器看一下新的地址：240e:3b4:303c:9790:1000:242:ac10:c802

更新一下dns记录到
240e:3b4:303c:9790:1000:242:ac10:c802

其它机器上ping
ping6 docker.lemonhall.me

ping不通

哦，我又忘了
sudo vim /etc/ndppd.conf
更新ndppd的配置

rules 到 240e:03b4:303c:9790:1000::/68

sudo systemctl restart ndppd

好了，ping通了，可以访问了，内网

ip138.com使用手机的网络给笔记本

https://docker.lemonhall.me:9443/

您的iP地址是：[183.46.44.5 ] 来自：中国广东 电信

哎呦，也就是说，路由器的静态地址配置都不需要了，这个好啊；

现在看有几个动态需要配置的点
=======================

a. docker里面那个daemon.json里，网桥网络对应的这个ipv6的网段是必须指定的，这个有点烦

b. 这个网段的配置值，也需要更新到ndppd的配置文件里面并且重启

c. 在docker的容器里面，需要再重启之后，去主动更新dns里的AAAA记录


a.b 其实就是[docker-ipv6](https://github.com/wido/docker-ipv6/) 这个项目要达成的

但可惜，这个项目太老了，有一些东西需要更新一下

b的话，需要重启docker之后，也有东西能够去触发这个脚本，这个再说

c，相对来说其实还好，有之前nas上的脚本的经验可以借鉴

配置三个动态的东西就可以了，OK

拆解那个脚本
==========

	[lemonhall@fedora36-macbook ~]$ command --help
	command: command [-pVv] 命令 [参数 ...]
	    执行一个简单命令或者显示命令的相关信息。

	    带 ARGS 参数运行 COMMAND 命令且抑制 shell 函数查询，或显示
	    指定的 COMMAND 命令的信息。可以在存在相同名称的函数定义的
	    情况下用于启动磁盘上的命令。

	    选项：
	      -p	使用 PATH 变量的一个默认值以确保所有的标准工具都能被找到。
	      -v	打印 COMMAND 命令的描述，和 `type' 内建相似
	      -V	打印每个 COMMAND 命令的详细描述

	    退出状态
	    返回 COMMAND 命令的返回状态，或者当找不到 COMMAND 命令时失败。
	[lemonhall@fedora36-macbook ~]$ command -v sipcalc
	/usr/bin/sipcalc
	[lemonhall@fedora36-macbook ~]$


sipcalc -s 255.255.255.254 -I wlp3s0

-[int-ipv4 : wlp3s0] - 0

[Split network]
Network			- 192.168.50.0    - 192.168.50.1
Network			- 192.168.50.2    - 192.168.50.3
Network			- 192.168.50.4    - 192.168.50.5
Network			- 192.168.50.6    - 192.168.50.7
Network			- 192.168.50.8    - 192.168.50.9
Network			- 192.168.50.10   - 192.168.50.11
Network			- 192.168.50.12   - 192.168.50.13
Network			- 192.168.50.14   - 192.168.50.15
Network			- 192.168.50.16   - 192.168.50.17
Network			- 192.168.50.18   - 192.168.50.19

这是ipv4的输出，我倒是大概明白了

https://docs.netgate.com/pfsense/en/latest/network/ipv6/subnets.html

阿西吧，用python吧

安装pip

https://pypi.org/project/subnet-utils/

sudo dnf install python3-pip

安装工具包
pip install subnet-utils
（这里可能有权限的坑，要注意一下）

network-divide 240e:3b4:303c:9790:18fe:fda0:9fcf:271c/64 16

[lemonhall@fedora36-macbook ~]$ network-divide 240e:3b4:303c:9790:18fe:fda0:9fcf:271c/64 16

CIDR:       240e:3b4:303c:9790::/68
Netmask:    ffff:ffff:ffff:ffff:f000::
Network:    240e:3b4:303c:9790::
Host Count: 1152921504606846976

CIDR:       240e:3b4:303c:9790:1000::/68
Netmask:    ffff:ffff:ffff:ffff:f000::
Network:    240e:3b4:303c:9790:1000::
Host Count: 1152921504606846976

CIDR:       240e:3b4:303c:9790:2000::/68
Netmask:    ffff:ffff:ffff:ffff:f000::
Network:    240e:3b4:303c:9790:2000::
Host Count: 1152921504606846976

CIDR:       240e:3b4:303c:9790:3000::/68
Netmask:    ffff:ffff:ffff:ffff:f000::
Network:    240e:3b4:303c:9790:3000::
Host Count: 1152921504606846976

CIDR:       240e:3b4:303c:9790:4000::/68
Netmask:    ffff:ffff:ffff:ffff:f000::
Network:    240e:3b4:303c:9790:4000::
Host Count: 1152921504606846976

emmm，这个输出我很喜欢


自己写了一个python脚本，来计算,write_prefix.py

运行后得到想要的那个输出

240e:3b4:303c:9790:1000::/68

他妈的，真心烦

我认为你可以通过虚拟环境得到你所需要的

您需要专门为该脚本创建一个虚拟环境。您将在该环境中使用正确的版本安装所需的所有软件包。只要在虚拟环境处于活动状态的情况下运行脚本，一切都将可用。-请参阅venv documenttion here

要创建虚拟环境，请运行python3 -m venv <your_venv_path>，路径为要存储虚拟环境的位置，例如~/.venvs/my_project/

要安装软件包，首先必须使其处于活动状态，然后运行pip

source <your_venv_path>/bin/activate
pip install png_util
到这里，您将准备好虚拟环境并安装软件包。如果在虚拟环境处于活动状态的情况下运行脚本，则包将可用

现在，因为您的脚本是一个守护进程this is how you make sure it runs within your virtual environment。基本上，虚拟环境在中创建一个Python副本，您只需在脚本中添加使用该Python“副本”的指令。只需添加#!<your_venv_path>/bin/python作为脚本的第一行即可

这样，当脚本运行时，它确实会在安装了所有软件包的虚拟环境中运行

PS：通过简单地以sudo的形式运行pip，可能所有东西都可以工作，因为它将在系统范围内安装软件包，使其可供所有用户使用。但是，由于它所造成的安全风险，这种选择是非常不受欢迎的，请参见此post with security risks of running sudo pip

希望这有帮助

搞定环境
====

mkdir ~/.venvs
mkdir ~/.venvs/docker

python3 -m venv ~/.venvs/docker
source ~/.venvs/docker/bin/activate

pip install subnet-utils

#!/root/.venvs/docker/bin/python

给python最上方加入这个就ok

然后chmod +x 给 脚本

sudo 执行就重启docker了

噢噢噢噢~~~

/home/lemonhall/docker/check_prefix_change.py

Docker IPv6 hook
The docker-ipv6 dhclient hook in this repository should be placed in /etc/dhcp/dhclient-enter-hooks.d/ where it will be executed after dhclient obtains a prefix.

The hook will get the first /80 subnet out of the delegated prefix and write it to /etc/docker/ipv6.prefix

The Docker daemon is then restarted so it will use the new subnet as the fixed IPv6 cidr.

Depending on your Ubuntu version (14.04 or 16.04) configuration has to be done differently due to the Upstart vs systemd changes. The end result is the same.

Afterwards you can print the processlist and see docker running with these arguments:

/usr/bin/docker daemon --ipv6 --fixed-cidr-v6=2001:00db8:100:0000:0000:0000:0000:0000/80

把我的两个文件copy过来

https://netbeez.net/blog/linux-dhcp-hooks-network-engineers/

OOO，我说呢

Variables
When a script is called by dhclient or dhcpcd, it has certain environment variables that are set by the hook mechanism. These variables hold values that have to do with how the network host is configured. To a certain extent the variable names are the same between dhclient and dhcpcd. This is very convenient if you are migrating from dhclient to dhcpcd or transferring scripts from one to the other. You might be able to use the same scripts without modifications – but always be sure to verify before you make the switch.

原来这个脚本里面的变量是来自于环境变量啊

好嘛

sudo systemctl status dhclient6-pd

好嘛~，根本就没有触发过的样子，我最担心的事情来了

这种机制的脚本不太好调试，说实话

总结一下
======

1、不需要静态路由

2、需要ndppd这个东西

3、需要在dhcp变化的时候有触发器，现在卡在这里了，脚本已经写好了，手动执行可以很好的重启docker了

4、还需要处理ndppd这玩意呢

5、最后还有每个docker里面需要定时上报AAAA记录的脚本呢

哎，别看事很不大，这一个个写起来，还挺费事了

6、处理ssl证书。。。

dhclient -6 -P -d wlp3s0

dhclient6-pd.service

	[Unit]
	Description=DHCPv6 Prefix Delegation client
	Wants=network.target network-online.target
	After=network.target network-online.target

	[Service]
	Type=simple
	Environment=NETWORK_INTERFACE=wlp3s0
	ExecStart=/sbin/dhclient -6 -P -d ${NETWORK_INTERFACE}
	Restart=always
	RestartSec=10s

	[Install]
	WantedBy=multi-user.target

cd /etc/systemd/system/
sudo vim dhclient6-pd.service

sudo systemctl daemon-reload
sudo systemctl start dhclient6-pd
sudo systemctl enable dhclient6-pd

闹心啊，

https://opensource.com/article/20/7/systemd-timers

# This service unit is for testing timer units
# By David Both
# Licensed under GPL V2
#

[Unit]
Description=Logs system statistics to the systemd journal
Wants=myMonitor.timer

[Service]
Type=oneshot
ExecStart=/usr/bin/free

[Install]
WantedBy=multi-user.target

# This timer unit is for testing
# By David Both
# Licensed under GPL V2
#

[Unit]
Description=Logs some system statistics to the systemd journal
Requires=myMonitor.service

[Timer]
Unit=myMonitor.service
OnCalendar=*-*-* *:*:00

[Install]
WantedBy=timers.target


放弃了
====
https://fedoramagazine.org/scheduling-tasks-with-cron/


dnf install cronie

crontab -e

	*/1 * * * * /etc/dhcp/dhclient-enter-hooks


systemctl start crond.service

		#!/bin/bash
		cd /etc/dhcp
		date >> log.txt
		source ~/.venvs/docker/bin/activate
		python check.py

脚本里面写四句话就好了，就每分钟检查一下吧，累了，毁灭吧

sudo systemctl restart ndppd

vim ndppd.conf

   rule

替换

import fileinput

filename = "/etc/ndppd.conf"

with fileinput.FileInput(filename, inplace = True, backup ='.bak') as f:
    for line in f:
        if("   rule" in line):
            print("   rule "+" new_ip "+"{", end ='\n')
        else:
            print(line, end='')

 sudo systemctl status ndppd

最后终于搞定了
===========

1、新建一个shell文件
#!/bin/bash

# For dhclient/dhclient-script debugging.
# Copy this into /etc/dhcp/ and make it executable.
# Run 'dhclient -d <interface>' to see info passed from dhclient to dhclient-script.
# See also HOOKS section in dhclient-script(8) man page.

cd /etc/dhcp

date >> log.txt

source ~/.venvs/docker/bin/activate

python check.py > env.log

其实就是初始化python的环境，以及打日志出来；

2、然后是
check.py
写的我差点怀疑人生
结果发现是crontab启动下的python下的os.system类的命令

无法继承当前的PATH，所以
        ipv6 = os.popen("/usr/sbin/ip addr show wlp3s0 | /usr/bin/grep '\<inet6\>' | /usr/bin/head -n1 | /usr/bin/awk '{ print $2 }' | /usr/bin/awk -F '/' '{ print $1 }'").read().strip()

 真是一行行的打印最后定位到的错误

3、初始化python环境就不多说啥了
mkdir ~/.venvs
mkdir ~/.venvs/docker

python3 -m venv ~/.venvs/docker
source ~/.venvs/docker/bin/activate

pip install subnet-utils

#!/root/.venvs/docker/bin/python

4、安装成crontab，记得是sudo su

https://fedoramagazine.org/scheduling-tasks-with-cron/


dnf install cronie

crontab -e

	*/1 * * * * /etc/dhcp/dhclient-enter-hooks



好了，以上就是，四步曲，完成

检测新的ip和老的ip之间是否有差异，有差异就修改docker的daemon.json和ndppd.conf两个文件

将计算好的新的网段地址，都更新到配置文件

并且重启两个服务

稍后开始写ddns更新AAAA记录的脚本

这个写完了以后系统就会聪明许多了

https://172.16.200.2:9443/

jH2U6s7s!^ZcYW7R








