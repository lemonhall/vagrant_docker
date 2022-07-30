<img width="1439" alt="image" src="https://user-images.githubusercontent.com/637919/181657954-36c8403f-e74e-4d97-b795-5ee72df6f803.png">

<img width="1194" alt="image" src="https://user-images.githubusercontent.com/637919/181657991-ce4a9d5a-f247-4986-9ce3-ab88b16111ce.png">

<img width="1160" alt="image" src="https://user-images.githubusercontent.com/637919/181862526-44b3c370-b190-4b3e-abb7-93d943936432.png">


### 参考资料：
https://blog.csdn.net/feiyu361/article/details/120284085

### 安装vb
略过，这没啥啊的，一路next

### 安装 vagrant

brew install vagrant

### 需要重启

### 查看状态

vagrant global-status

### 看看仓库
https://app.vagrantup.com/boxes/search

https://app.vagrantup.com/generic/boxes/fedora36


### 初始化文件

vagrant init generic/fedora36

### 拉起虚拟机

vagrant up

	(base) lemonhall@yuningdeMBP:~/vagrant$ vagrant init generic/fedora36
	A `Vagrantfile` has been placed in this directory. You are now
	ready to `vagrant up` your first virtual environment! Please read
	the comments in the Vagrantfile as well as documentation on
	`vagrantup.com` for more information on using Vagrant.
	(base) lemonhall@yuningdeMBP:~/vagrant$ vagrant up
	Bringing machine 'default' up with 'virtualbox' provider...
	==> default: Box 'generic/fedora36' could not be found. Attempting to find and install...
	    default: Box Provider: virtualbox
	    default: Box Version: >= 0
	==> default: Loading metadata for box 'generic/fedora36'
	    default: URL: https://vagrantcloud.com/generic/fedora36
	==> default: Adding box 'generic/fedora36' (v4.1.0) for provider: virtualbox
	    default: Downloading: https://vagrantcloud.com/generic/boxes/fedora36/versions/4.1.0/providers/virtualbox.box
	Progress: 64% (Rate: 21.9M/s, Estimated time remaining: 0:00:25)

### 拿到虚拟机链接
vargrant ssh

### 更新系统

dnf update 

### 在虚拟机里安装docker

https://docs.docker.com/engine/install/fedora/

### 插入新的源
sudo dnf -y install dnf-plugins-core

sudo dnf config-manager \
    --add-repo \
    https://download.docker.com/linux/fedora/docker-ce.repo


### 安装引擎本身

sudo dnf install docker-ce docker-ce-cli containerd.io docker-compose-plugin

### 启动docker

sudo systemctl start docker

### 看看状态
	[vagrant@fedora36 ~]$ sudo systemctl status docker
	● docker.service - Docker Application Container Engine
	     Loaded: loaded (/usr/lib/systemd/system/docker.service; disabled; vendor preset: disabled)
	     Active: active (running) since Thu 2022-07-28 23:00:31 UTC; 6s ago
	TriggeredBy: ● docker.socket
	       Docs: https://docs.docker.com
	   Main PID: 27061 (dockerd)
	      Tasks: 8
	     Memory: 28.3M
	        CPU: 149ms
	     CGroup: /system.slice/docker.service
	             └─ 27061 /usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock

	Jul 28 23:00:31 fedora36.localdomain dockerd[27061]: time="2022-07-28T23:00:31.308050643Z" level=info msg="ccResolverWrapper: sending update to cc: {[{unix:///run/containerd/containerd.sock  <nil> 0 >
	Jul 28 23:00:31 fedora36.localdomain dockerd[27061]: time="2022-07-28T23:00:31.308059740Z" level=info msg="ClientConn switching balancer to \"pick_first\"" module=grpc
	Jul 28 23:00:31 fedora36.localdomain dockerd[27061]: time="2022-07-28T23:00:31.354193075Z" level=info msg="Loading containers: start."
	Jul 28 23:00:31 fedora36.localdomain dockerd[27061]: time="2022-07-28T23:00:31.724656918Z" level=info msg="Default bridge (docker0) is assigned with an IP address 172.17.0.0/16. Daemon option --bip c>
	Jul 28 23:00:31 fedora36.localdomain dockerd[27061]: time="2022-07-28T23:00:31.795825115Z" level=info msg="Firewalld: interface docker0 already part of docker zone, returning"
	Jul 28 23:00:31 fedora36.localdomain dockerd[27061]: time="2022-07-28T23:00:31.884090169Z" level=info msg="Loading containers: done."
	Jul 28 23:00:31 fedora36.localdomain dockerd[27061]: time="2022-07-28T23:00:31.911463057Z" level=info msg="Docker daemon" commit=a89b842 graphdriver(s)=overlay2 version=20.10.17
	Jul 28 23:00:31 fedora36.localdomain dockerd[27061]: time="2022-07-28T23:00:31.911630128Z" level=info msg="Daemon has completed initialization"
	Jul 28 23:00:31 fedora36.localdomain systemd[1]: Started docker.service - Docker Application Container Engine.
	Jul 28 23:00:31 fedora36.localdomain dockerd[27061]: time="2022-07-28T23:00:31.937260904Z" level=info msg="API listen on /run/docker.sock"
	[vagrant@fedora36 ~]$

### 跑个测试

sudo docker run hello-world

	[vagrant@fedora36 ~]$ sudo docker run hello-world
	Unable to find image 'hello-world:latest' locally
	latest: Pulling from library/hello-world
	2db29710123e: Pull complete
	Digest: sha256:53f1bbee2f52c39e41682ee1d388285290c5c8a76cc92b42687eecf38e0af3f0
	Status: Downloaded newer image for hello-world:latest

	Hello from Docker!
	This message shows that your installation appears to be working correctly.

	To generate this message, Docker took the following steps:
	 1. The Docker client contacted the Docker daemon.
	 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
	    (amd64)
	 3. The Docker daemon created a new container from that image which runs the
	    executable that produces the output you are currently reading.
	 4. The Docker daemon streamed that output to the Docker client, which sent it
	    to your terminal.

	To try something more ambitious, you can run an Ubuntu container with:
	 $ docker run -it ubuntu bash

	Share images, automate workflows, and more with a free Docker ID:
	 https://hub.docker.com/

	For more examples and ideas, visit:
	 https://docs.docker.com/get-started/

	[vagrant@fedora36 ~]$ docker ps
	Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.24/containers/json": dial unix /var/run/docker.sock: connect: permission denied
	[vagrant@fedora36 ~]$ sudo docker ps
	CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
	[vagrant@fedora36 ~]$

这就很好嘛

有全部掌控权的虚拟机还是感觉更好啊


### 装个门户吧

#### 拉镜像
sudo docker pull portainer/portainer-ce

#### 看文档
https://docs.portainer.io/start/install/server/docker/linux

#### 建一个新的卷
sudo docker volume create portainer_data

#### 启容器
sudo docker run -d -p 8000:8000 -p 9443:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest

### 关掉虚拟机
vagrant halt


### 打开配置文件

	# Create a public network, which generally matched to bridged network.
	# Bridged networks make the machine appear as another physical device on
	# your network.
	config.vm.network "public_network"

把这一段直接打开

###

(base) lemonhall@yuningdeMBP:~/vagrant$ vagrant up
Bringing machine 'default' up with 'virtualbox' provider...
==> default: Checking if box 'generic/fedora36' version '4.1.0' is up to date...
==> default: Clearing any previously set forwarded ports...
==> default: Clearing any previously set network interfaces...
==> default: Available bridged network interfaces:
1) en0: Wi-Fi
2) en5: USB Ethernet(?)
3) ap1
4) awdl0
5) llw0
6) en3: 雷雳3
7) en4: 雷雳4
8) en2: 雷雳2
9) en1: 雷雳1
10) bridge0
==> default: When choosing an interface, it is usually the one that is
==> default: being used to connect to the internet.
==> default:
    default: Which interface should the network bridge to? 1

ifconfig eth1 192.168.50.117 netmask 255.255.255.0 up


### 实验了许多次，最后发现只能手动指定

https://www.vagrantup.com/docs/networking/public_network

	  # Create a public network, which generally matched to bridged network.
	  # Bridged networks make the machine appear as another physical device on
	  # your network.
	  config.vm.network "public_network",auto_config: false,bridge: "en0: Wi-Fi"

	  # manual ip
	  config.vm.provision "shell",
	    run: "always",
	    inline: "ifconfig eth1 192.168.50.117 netmask 255.255.255.0 up"

### 然后把docker设定为自动启动

sudo systemctl enable docker

### 访问
https://192.168.50.117:9443/#!/init/admin

### 用户密码
https://192.168.50.51:9443/#!/2/docker/dashboard

jH2U6s7s!^ZcYW7R


### 看一下网络咯
	[vagrant@fedora36 ~]$ ifconfig
	docker0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
	        inet 172.17.0.1  netmask 255.255.0.0  broadcast 172.17.255.255
	        ether 02:42:83:5a:dd:05  txqueuelen 0  (Ethernet)
	        RX packets 1382  bytes 4383477 (4.1 MiB)
	        RX errors 0  dropped 0  overruns 0  frame 0
	        TX packets 2607  bytes 388387 (379.2 KiB)
	        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

	eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
	        inet 10.0.2.15  netmask 255.255.255.0  broadcast 10.0.2.255
	        ether 08:00:27:1e:19:c3  txqueuelen 1000  (Ethernet)
	        RX packets 835  bytes 280043 (273.4 KiB)
	        RX errors 0  dropped 0  overruns 0  frame 0
	        TX packets 606  bytes 78356 (76.5 KiB)
	        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

	eth1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
	        inet 192.168.50.117  netmask 255.255.255.0  broadcast 192.168.50.255
	        inet6 240e:3b4:3034:4e30:2157:80a7:d446:4f23  prefixlen 64  scopeid 0x0<global>
	        inet6 fe80::a029:db8f:5648:12fc  prefixlen 64  scopeid 0x20<link>
	        ether 08:00:27:cf:27:bb  txqueuelen 1000  (Ethernet)
	        RX packets 2797  bytes 216145 (211.0 KiB)
	        RX errors 0  dropped 0  overruns 0  frame 0
	        TX packets 3579  bytes 4559374 (4.3 MiB)
	        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

	lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
	        inet 127.0.0.1  netmask 255.0.0.0
	        loop  txqueuelen 1000  (Local Loopback)
	        RX packets 2  bytes 292 (292.0 B)
	        RX errors 0  dropped 0  overruns 0  frame 0
	        TX packets 2  bytes 292 (292.0 B)
	        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

	veth89ea08b: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
	        ether 3a:f3:b1:cb:e2:45  txqueuelen 0  (Ethernet)
	        RX packets 1382  bytes 4402825 (4.1 MiB)
	        RX errors 0  dropped 0  overruns 0  frame 0
	        TX packets 2607  bytes 388387 (379.2 KiB)
	        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

	[vagrant@fedora36 ~]$

### 修改一下颜色
vim ~/.bashrc

export PS1="\[\e[32m\][\[\e[m\]\[\e[31m\]\u\[\e[m\]\[\e[33m\]@\[\e[m\]\[\e[32m\]\h\[\e[m\]:\[\e[36m\]\w\[\e[m\]\[\e[32m\]]\[\e[m\]\[\e[32;47m\]\\$\[\e[m\] "

很丑，但是能强调这是虚拟机

因为从这里面打开容器的时候可又是绿色的了

### 就无语

https://stackoverflow.com/questions/39374557/mac-os-x-route-gateway-link5

	Destination        Gateway            Flags           Netif Expire
	default            192.168.50.1       UGScg             en0
	127                127.0.0.1          UCS               lo0
	127.0.0.1          127.0.0.1          UH                lo0
	169.254            link#6             UCS               en0      !
	192.168.50         link#6             UCS               en0      !
	192.168.50.1/32    link#6             UCS               en0      !
	192.168.50.1       b0:6e:bf:28:92:c0  UHLWIir           en0   1199
	192.168.50.84/32   link#6             UCS               en0      !
	192.168.50.117     8:0:27:cf:27:bb    UHLWI             en0    503
	192.168.50.138     38:f9:d3:1a:72:78  UHLWIi            en0    629
	192.168.50.188     7a:eb:3e:16:cf:6b  UHLWIi            en0   1010
	192.168.50.233     90:9:d0:d:e7:ed    UHLWIi            en0    965
	192.168.50.238     8c:aa:b5:6d:fd:34  UHLWI             en0   1200
	224.0.0/4          link#6             UmCS              en0      !
	224.0.0.251        1:0:5e:0:0:fb      UHmLWI            en0
	239.255.255.250    1:0:5e:7f:ff:fa    UHmLWI            en0
	255.255.255.255/32 link#6             UCS               en0      !

netstat -nr

第六个就是ifconfig数出来的第六个，就是en0

	[vagrant@fedora36:~]$ route -n
	Kernel IP routing table
	Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
	0.0.0.0         192.168.50.1    0.0.0.0         UG    0      0        0 eth1
	10.0.2.0        0.0.0.0         255.255.255.0   U     101    0        0 eth0
	172.17.0.0      0.0.0.0         255.255.0.0     U     0      0        0 docker0
	192.168.50.0    0.0.0.0         255.255.255.0   U     0      0        0 eth1

这边是用route -n

https://unix.stackexchange.com/questions/94018/what-is-the-meaning-of-0-0-0-0-as-a-gateway#:~:text=Therefore%2C%200.0.,interface%20to%20reach%20that%20router.

sudo route del -net 192.168.50.0 gw 0.0.0.0 netmask 255.255.255.0 dev eth1

ip route add 192.168.50.0/24 via 192.168.50.1 dev eth1

ip route add 192.168.50.1 dev eth1
ip route add default via 192.168.50.1

arp -s 192.168.50.1 -i eth1 b0:6e:bf:28:92:c0
arp -s _gateway -i eth1 b0:6e:bf:28:92:c0


38:F9:D3:9D:5A:D2

git config --global http.proxy http://192.168.50.232:13128


### 切记一件事

就是这个vagrant如果要用网桥的话，必须走有线网络，wifi有bug
