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

