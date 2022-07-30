<img width="1160" alt="image" src="https://user-images.githubusercontent.com/637919/181862526-44b3c370-b190-4b3e-abb7-93d943936432.png">

![image](https://user-images.githubusercontent.com/637919/181862535-97ac8add-9526-43bd-a5ad-9cb13fc341a3.png)

![image](https://user-images.githubusercontent.com/637919/181862545-8ed520c4-6850-49f4-bb7e-a69690660228.png)


### 参考资料
https://www.csdn.net/tags/MtTaMg4sMDQwMDQxLWJsb2cO0O0O.html


一般情况下，Docker创建一个容器的时候，会具体执行如下操作：

1.创建一对虚拟接口，分别放到本地主机和新容器的命名空间中；

2.本地主机一端的虚拟接口连接到默认的docker0网桥或指定网桥上，并具有一个以veth开头的唯一名字，如veth1234；

3.容器一端的虚拟接口将放到新创建的容器中，并修改名字作为eth0。这个接口只在容器的命名空间可见；

4.从网桥可用地址段中获取一个空闲地址分配给容器的eth0（例如172.17.0.2/16），并配置默认路由网关为docker0网卡的内部接口docker0的IP地址（例如172.17.42.1/16）。

完成这些之后，容器就可以使用它所能看到的eth0虚拟网卡来连接其他容器和访问外部网络。用户也可以通过docker network命令来手动管理网络。


1）bridge模式，--net=bridge(默认)
这是dokcer网络的默认设置，为容器创建独立的网络命名空间，容器具有独立的网卡等所有单独的网络栈，是最常用的使用方式。
在docker run启动容器的时候，如果不加--net参数，就默认采用这种网络模式。安装完docker，系统会自动添加一个供docker使用的网桥docker0，我们创建一个新的容器时，
容器通过DHCP获取一个与docker0同网段的IP地址，并默认连接到docker0网桥，以此实现容器与宿主机的网络互通。
 
2）host模式，--net=host
这个模式下创建出来的容器，直接使用容器宿主机的网络命名空间。
将不拥有自己独立的Network Namespace，即没有独立的网络环境。它使用宿主机的ip和端口。
 
3）none模式，--net=none
为容器创建独立网络命名空间，但不为它做任何网络配置，容器中只有lo，用户可以在此基础上，对容器网络做任意定制。
这个模式下，dokcer不为容器进行任何网络配置。需要我们自己为容器添加网卡，配置IP。
因此，若想使用pipework配置docker容器的ip地址，必须要在none模式下才可以。
 
4）其他容器模式（即container模式），--net=container:NAME_or_ID
与host模式类似，只是容器将与指定的容器共享网络命名空间。
这个模式就是指定一个已有的容器，共享该容器的IP和端口。除了网络方面两个容器共享，其他的如文件系统，进程等还是隔离开的。
 
5）用户自定义：docker 1.9版本以后新增的特性，允许容器使用第三方的网络实现或者创建单独的bridge网络，提供网络隔离能力。


https://cloud.tencent.com/developer/article/1587094

从上面的网络模型可以看出，容器从原理上是可以与宿主机乃至外界的其他机器通信的。同一宿主机上，容器之间都是连接掉docker0这个网桥上的，它可以作为虚拟交换机使容器可以相互通信。
然而，由于宿主机的IP地址与容器veth pair的 IP地址均不在同一个网段，故仅仅依靠veth pair和namespace的技术，还不足以使宿主机以外的网络主动发现容器的存在。为了使外界可以方位容器中的进程，docker采用了端口绑定的方式，也就是通过iptables的NAT，将宿主机上的端口
端口流量转发到容器内的端口上。


举一个简单的例子，使用下面的命令创建容器，并将宿主机的3306端口绑定到容器的3306端口：
docker run -tid --name db -p 3306:3306 MySQL
 
在宿主机上，可以通过iptables -t nat -L -n，查到一条DNAT规则：
 
DNAT tcp -- 0.0.0.0/0 0.0.0.0/0 tcp dpt:3306 to:172.17.0.5:3306
 
上面的172.17.0.5即为bridge模式下，创建的容器IP。
 
很明显，bridge模式的容器与外界通信时，必定会占用宿主机上的端口，从而与宿主机竞争端口资源，对宿主机端口的管理会是一个比较大的问题。同时，由于容器与外界通信是基于三层上iptables NAT，性能和效率上的损耗是可以预见的。


各项配置如下：

主机1的IP地址为：192.168.91.128
主机2的IP地址为：192.168.91.129
为主机1上的Docker容器分配的子网：10.0.128.0/24
为主机2上的Docker容器分配的子网：10.0.129.0/24
这样配置之后，两个主机上的Docker容器就肯定不会使用相同的IP地址从而避免了IP冲突。

我们接下来 定义两条路由规则 即可：

所有目的地址为10.0.128.0/24的包都被转发到主机1上
所有目的地址为10.0.129.0/24的包都被转发到主机2上
综上所述，数据包在两个容器间的传递过程如下：

从container1 发往 container2 的数据包，首先发往container1的“网关”docker0，然后通过查找主机1的路由得知需要将数据包发给主机2，数据包到达主机2后再转发给主机2的docker0，最后由其将数据包转到container2中；反向原理相同，不再赘述。
我们心里方案想的是这样，接下来实践一下看看是否可行。

编辑主机1上的 /etc/default/docker 文件，最后一行添加
DOCKER_OPTS="--bip 10.0.129.1/24"


主机1上：
root@ubuntu:~ route -n

	Kernel IP routing table
	Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
	0.0.0.0         192.168.91.2    0.0.0.0         UG    0      0        0 ens32
	10.0.128.0      0.0.0.0         255.255.255.0   U     0      0        0 docker0
	192.168.91.0    0.0.0.0         255.255.255.0   U     0      0        0 ens32

默认只有自己本身的路由，如果需要访问 10.0.129.0/24 网段，需要添加路由

route add -net 10.0.129.0/24 gw 192.168.91.129

root@ubuntu:~ route -n

	Kernel IP routing table
	Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
	0.0.0.0         192.168.91.2    0.0.0.0         UG    0      0        0 ens32
	10.0.128.0      0.0.0.0         255.255.255.0   U     0      0        0 docker0
	10.0.129.0      192.168.91.129  255.255.255.0   UG    0      0        0 ens32
	192.168.91.0    0.0.0.0         255.255.255.0   U     0      0        0 ens32

主机2：

route add -net 10.0.128.0/24 gw 192.168.91.128

在主机1上，ping主机2的docker0地址

	root@ubuntu:~# ping 10.0.129.1 -c 1
	PING 10.0.129.1 (10.0.129.1) 56(84) bytes of data.
	bytes from 10.0.129.1: icmp_seq=1 ttl=64 time=1.35 ms

	--- 10.0.129.1 ping statistics ---
	packets transmitted, 1 received, 0% packet loss, time 0ms
	rtt min/avg/max/mdev = 1.355/1.355/1.355/0.000 ms

在主机2上，ping主机1的docker0地址

	root@ubuntu:~# ping 10.0.128.1 -c 1
	PING 10.0.128.1 (10.0.128.1) 56(84) bytes of data.
	bytes from 10.0.128.1: icmp_seq=1 ttl=64 time=1.73 ms

	--- 10.0.128.1 ping statistics ---
	packets transmitted, 1 received, 0% packet loss, time 0ms
	rtt min/avg/max/mdev = 1.732/1.732/1.732/0.000 ms


ok，既然docker0都通了，那么起一个docker容器，会不会也是通的的呢？测试一下吧

在主机1上面启动一个容器，这里选用apline镜像，它只有4.5M，并且自带ping命令！

先查看ip地址

从结果中，可以发现。docker0是通的，但是主机2中的容器是不通的，为什么呢？

1）首先宿主机上创建一对虚拟网卡veth pair设备，veth设备总是成对出现的，形成一个通信通道，数据传输就是基于这个链路的，veth设备常用来连接两个网络设备

2）Docker将veth pair设备的一端放在容器中，并命名为eth0,然后将另一端加入docker0网桥中，可以通过brctl show命令查看

3）从docker0字网卡中分配一个IP到给容器使用，并设置docker0的IP地址为容器默认网关

4）此时容器IP与宿主机是可以通信的，宿主机也可以访问容器中的ip地址，在bridge模式下，连接同一网桥的容器之间可以相互通信，同时容器可以访问外网，但是其他物理机不能访问docker容器IP，需要通过NAT将容器的IP的port映射为宿主机的IP和port；

会发现有一个 veth077daec 的网卡设备。咦，这是个啥？

当运行docker容器后，再次执行ifconfig命令可以看到会多出个网卡驱动veth开头的名字，所以补充下veth。

veth
Linux container 中用到一个叫做veth的东西，这是一种新的设备，专门为 container 所建。veth 从名字上来看是 Virtual ETHernet 的缩写，它的作用很简单，就是要把从一个 network namespace 发出的数据包转发到另一个 namespace。veth 设备是成对的，一个是 container 之中，另一个在 container 之外，即在真实机器上能看到的。 
VETH设备总是成对出现，一端请求发送的数据总是从另一端以请求接受的形式出现。创建并配置正确后，向其一端输入数据，VETH会改变数据的方向并将其送入内核网络子系统，完成数据的注入，而在另一端则能读到此数据。（Namespace，其中往veth设备上任意一端上RX到的数据，都会在另一端上以TX的方式发送出去）veth工作在L2数据链路层，veth-pair设备在转发数据包过程中并不串改数据包内容。 

成数据的注入，而在另一端则能读到此数据。（Namespace，其中往veth设备上任意一端上RX到的数据，都会在另一端上以TX的方式发送出去）veth工作在L2数据链路层，veth-pair设备在转发数据包过程中并不串改数据包内容。 
显然，仅有veth-pair设备，容器是无法访问网络的。因为容器发出的数据包，实质上直接进入了veth1设备的协议栈里。如果容器需要访问网络，需要使用bridge等技术，将veth1接收到的数据包通过某种方式转发出去 。 
veth参考链接：http://blog.csdn.net/sld880311/article/details/77650937


因此，如果要多台主机之间的docker通信，需要使用NAT转换。那么接下来，就是设置iptables规则了！

主机1
在主机1上查看默认的nat 规则

	root@ubuntu:~# iptables -t nat -LChain PREROUTING (policy ACCEPT)
	target     prot opt source               destination
	DOCKER     all  --  anywhere             anywhere             ADDRTYPE match dst-type LOCAL

	Chain INPUT (policy ACCEPT)
	target     prot opt source               destination

	Chain OUTPUT (policy ACCEPT)
	target     prot opt source               destination
	DOCKER     all  --  anywhere            !127.0.0.0/8          ADDRTYPE match dst-type LOCAL

	Chain POSTROUTING (policy ACCEPT)
	target     prot opt source               destination
	MASQUERADE  all  --  10.0.128.0/24        anywhere

	Chain DOCKER (2 references)
	target     prot opt source               destination
	RETURN     all  --  anywhere             anywhere


这些nat规则，都是docker帮你做的。

增加一条规则

iptables -t nat -I PREROUTING -s 10.0.128.0/24 -d 10.0.129.0/24 -j DNAT --to 10.0.128.1

PREROUTING:可以在这里定义进行目的NAT的规则，因为路由器进行路由时只检查数据包的目的ip地址，所以为了使数据包得以正确路由，我们必须在路由之前就进行目的NAT;

上面那一条路由规则是啥意思呢？就是当源地址为10.0.128.0/24网段 访问 10.0.129.0/24 时，在路由之前，将ip转换为10.0.128.1。

主机1的IP地址为：192.168.91.128
主机2的IP地址为：192.168.91.129
为主机1上的Docker容器分配的子网：10.0.128.0/24
为主机2上的Docker容器分配的子网：10.0.129.0/24

注意：一定要加-d参数。如果不加，虽然docker之间可以互通，但是不能访问网站，比如百度，qq之类的！

为什么呢？访问10.0.129.0/24 时，通过docker0网卡出去的。但是访问百度，还是通过docker0，就出不去了！

真正连接外网的是ens32网卡，必须通过它才行！因此必须要指定-d参数！

是可以通讯的！

注意：iptables必须在 PREROUTING 上面做，而不是常规的 POSTROUTING。我测试在POSTROUTING做规则，始终无法通讯！


主机2
主机2上添加如下规则：

iptables -t nat -I PREROUTING -s 10.0.129.0/24 -d 10.0.128.0/24 -j DNAT --to 10.0.129.1

也是可以通讯的！

注意：如果发现还是不通，重启一下docker服务，应该就可以了！


五、3台主机测试

上面已经实现了2台docker之间的通信，如果是3台呢？怎么搞？还是一样的。

只不过每台主机都要增加2条路由规则以及2条iptables规则。

做路由规则时，容器搞混淆，为了避免这种问题，做一个一键脚本就可以了！

	#!/bin/bash

	# 主机ip后缀清单
	hosts="128 129 131"

	# 循环主机
	for i in `echo $hosts`;do
	    # 写入临时文件
	    cat >/tmp/dockerc<<EOF
	    DOCKER_OPTS=\"--bip 10.0.$i.1/24\"
	EOF
	    # 远程执行命令,更改docker0网段
	    ssh 192.168.91.$i "echo $(cat /tmp/dockerc)>> /etc/default/docker"
	    # 重启docker服务
	    ssh 192.168.91.$i "systemctl restart docker"
	    # 清空nat规则
	    # ssh 192.168.91.$i "sudo iptables -t nat -F"

	    # 再次循环
	    for j in `echo $hosts`;do
	        # 排除自身
	        if [ "$j" != "$i" ];then
	            # 添加路由
	            ssh 192.168.91.$i "route add -net 10.0.$j.0/24 gw 192.168.91.$j"
	            # 添加nat规则
	            ssh 192.168.91.$i "iptables -t nat -I PREROUTING -s 10.0.$i.0/24 -d 10.0.$j.0/24 -j DNAT --to 10.0.$i.1"
	        fi
	    done
	    # 重启docker服务,写入默认的nat规则
	    ssh 192.168.91.$i "systemctl restart docker"
	done



=========
加完路由后，A主机到B主机的docker0能ping通，但是B主机的容器ping不通，你这样加DNAT转换不对，等于把所有到容器的请求都转到docker0了，所以能ping通，不信可以随便ping docker0网段不存的IP。正常加完route应该就是通的。如果不通可能是因为在B主机的forward链被drop了（这种情况我在ubuntu主机遇见过，ubu你说的对。我看了下，网上都是这个文档，简直太骗人了ntu主机默认是drop，redhat默认是ACCEPT，就没问题）。

你说的对。我看了下，网上都是这个文档，简直太骗人了

厉害了！! 的确如此！route add完之后，如果不能ping通，使用iptables -P -l查看forward链，如果是drop状态的，那么使用sudo iptables -t filter -P FORWARD ACCEPT设置为ACCEPT，成功！！感谢楼主！

确实有问题，看https://blog.csdn.net/NewTyun/article/details/104191062

压根不用配iptables

============
https://blog.csdn.net/NewTyun/article/details/104191062

实战|两种常用的跨主机Docker容器互通方法

============
https://garutilorenzo.github.io/a-bash-solution-for-docker-and-iptables-conflict/

https://docs.docker.com/network/iptables/

Add iptables policies before Docker’s rules
Docker installs two custom iptables chains named DOCKER-USER and DOCKER, and it ensures that incoming packets are always checked by these two chains first.

All of Docker’s iptables rules are added to the DOCKER chain. Do not manipulate this chain manually. If you need to add rules which load before Docker’s rules, add them to the DOCKER-USER chain. These rules are applied before any rules Docker creates automatically.

Rules added to the FORWARD chain -- either manually, or by another iptables-based firewall -- are evaluated after these chains. This means that if you expose a port through Docker, this port gets exposed no matter what rules your firewall has configured. If you want those rules to apply even when a port gets exposed through Docker, you must add these rules to the DOCKER-USER chain.

Docker on a router🔗
Docker also sets the policy for the FORWARD chain to DROP. If your Docker host also acts as a router, this will result in that router not forwarding any traffic anymore. If you want your system to continue functioning as a router, you can add explicit ACCEPT rules to the DOCKER-USER chain to allow it:

 iptables -I DOCKER-USER -i src_if -o dst_if -j ACCEPT

 =======
 https://iximiuz.com/en/posts/container-networking-is-simple/
 这一篇很好

 =======
 https://www.digitalocean.com/community/tutorials/how-to-list-and-delete-iptables-firewall-rules

 iptables太恶心了

 sudo iptables -L --line-numbers


 route add -net 172.17.0.0/24 gw 192.168.50.51

 mac下
 sudo route -n add -net 172.17.0.0/24  192.168.50.51


安装tcpdump
dnf install tcpdump

https://forum.free5gc.org/t/not-able-to-access-container-ip-from-outer-network-icmp-request-ping-is-not-reaching-container/1233/12

sudo tcpdump -n -i any icmp


=====================
Well, I figured it out. And it's a doozy.

CentOS 8 uses nftables, which by itself isn't surprising. It ships with the nft version of the iptables commands, which means when you use the iptables command it actually maintains a set of compatibility tables in nftables.

However...

Firewalld -- which is installed by default -- has native support for nftables, so it doesn't make use of the iptables compatibility layer.

So while iptables -S INPUT shows you:

# iptables -S INPUT
-P INPUT ACCEPT
What you actually have is:

        chain filter_INPUT {
                type filter hook input priority 10; policy accept;
                ct state established,related accept
                iifname "lo" accept
                jump filter_INPUT_ZONES_SOURCE
                jump filter_INPUT_ZONES
                ct state invalid drop
                reject with icmpx type admin-prohibited  <-- HEY LOOK AT THAT!
        }
The solution here (and honestly probably good advice in general) is:

systemctl disable --now firewalld
With firewalld out of the way, the iptables rules visible with iptables -S will behave as expected.

https://unix.stackexchange.com/questions/552857/why-are-my-network-connections-being-rejected

=============
sudo systemctl disable --now firewalld

我累个大槽，原来fedora和centos 8以后用了一个叫firewalld的鬼玩意

然后删掉自启动后

(base) lemonhall@yuningdeMBP:~$ ping 172.17.0.3
PING 172.17.0.3 (172.17.0.3): 56 data bytes
64 bytes from 172.17.0.3: icmp_seq=0 ttl=63 time=2.973 ms
64 bytes from 172.17.0.3: icmp_seq=1 ttl=63 time=4.469 ms
64 bytes from 172.17.0.3: icmp_seq=2 ttl=63 time=2.258 ms
64 bytes from 172.17.0.3: icmp_seq=3 ttl=63 time=3.318 ms
64 bytes from 172.17.0.3: icmp_seq=4 ttl=63 time=4.942 ms
64 bytes from 172.17.0.3: icmp_seq=5 ttl=63 time=2.243 ms
64 bytes from 172.17.0.3: icmp_seq=6 ttl=63 time=7.526 ms
^C
--- 172.17.0.3 ping statistics ---
7 packets transmitted, 7 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = 2.243/3.961/7.526/1.739 ms
(base) lemonhall@yuningdeMBP:~$

一路顺畅

我嘞个大去，原来还是防火墙的问题

不熟悉fedora啊

好吧

===========
容器里面出不去
1、vagrant的网络配置里，其实可以把默认路由干掉
2、可以给docker0上加路由规则

sudo route add -n 0.0.0.0/24 gw 192.168.50.1 dev docker0
sudo route add default gw 192.168.50.1 docker0

给docker0加不上这个路由啊
算了

sudo route del default gw 10.0.2.2 eth0

删掉eth0那个碍事的路由也行

本来这个可以在vagranfile里解决的，行吧

然后容器网络正常了


最终总结
=======

https://github.com/lemonhall/vagrant_docker/blob/main/README_ip_v6.md
将近20个小时的瞎折腾
结果最后其实非常简单

一台物理机，一个虚拟机（vagrant管理的fedora36），一个docker，一个物理的路由
1、拿地址
让Host宿主机要有一个与物理路由器同网段的地址，这样，它才能被路由器get到
方法是，桥接网络，vm里面的，桥接把我坑了4-5个小时的地方其实就一个
【vb的桥接，对wifi的那个nic支持不好，具体原因可以深化】
所以，你需要一个有限cable的网络nic去桥接
好了，这样host就拿到一个192.168.50.xxx的ip地址了，可以在路由器里看到它了
2、配路由
每一个Host机器上的容器，其实都可以有一个子网，比如172.18.xx.xx,255.255.0.0
那么，不需要去看网上大多数流传的那种静态路由的配置方式，因为那样的话，每台主机都要配静态路由表，太累了，路由器有这个功能的
如下，有几个主机，配置几个子网就行了，把host主机视为一个路由器就可以理解了
3、主机上侦听
sudo tcpdump -n -i any icmp
这一步卡了我很久
就看了好多文章，静下心来还看了很多docker默认的iptables的规则问题，等等等等
我的问题在于，清空了iptables之后，还是只能ping 成功 docker0的那个172.17.0.1
最后忽然用tcpdump一层层排查后才意识到，还是有什么东西挡着我
sudo systemctl disable --now firewalld
最后才明白，fedora和centos最新的版本做了一个新的防火墙，干掉就完了，内网搞这些干啥
4、最后成功
5、遗留
似乎访问外网不成功，稍后看一下怎么回事
===========
容器里面出不去
1、vagrant的网络配置里，其实可以把默认路由干掉
2、可以给docker0上加路由规则
sudo route add -n 0.0.0.0/24 gw 192.168.50.1 dev docker0
sudo route add default gw 192.168.50.1 docker0
给docker0加不上这个路由啊
算了
sudo route del default gw 10.0.2.2 eth0
删掉eth0那个碍事的路由也行
本来这个可以在vagranfile里解决的，行吧
然后容器网络正常了


### 删默认路由

  # default router
  config.vm.provision "shell",
    run: "always",
    inline: "ip route del default via 10.0.2.2 || true"


### 配置裸机器的docker

sudo vim /etc/docker/daemon.json


{
  "bip": "172.16.200.1/24"
}

重启服务

sudo systemctl restart docker

到路由器里面去

配置一条
172.16.200.0 mask 255.255.255.0 gw 192.168.50.12 
的路由规则

然后直接干掉防火墙
sudo systemctl disable --now firewalld

然后我看了FORWARD默认是drop
sudo iptables -P FORWARD ACCEPT

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
