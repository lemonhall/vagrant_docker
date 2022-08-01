ipv6+dhcp-dp+ndp+dockder+dns
============================

环境
====
* fedora36物理机
* 5.18的内核
* docker官方版本
* 电信网络，ipv6全开，有LAN global，也大于/80，可以继续划子网


脚本
===
核心是check.py

逻辑大约如下：

1)检查当前物理机器的ip地址，写入一个文本文件，由crontab拉起（root），间隔时间内两者做对比，如果有任何变化:
	2)打开/etc/docker/daemon.json文件，修改里面的fixed-cidr-v6值为prefix
	3)prefix的计算，是将当前网络做/68级别的划分并取了第二个网段
	4)如果有第二台物理机，安全起见，需要配置为第三个网段

	5)重启docker的服务，这样所有容器重新启动，并获得配置好了的ipv6地址

	6)修改/etc/ndppd.conf内rule的值，为prefix
	7)同样的，重启

	8)完成重启工作之后，获取docker所有的命名容器，并将name作为dns域名的二级域名，将ip地址作为AAAA记录的值上报
	9)更新dns记录
ELSE:
	什么都不做

这就是核心的逻辑

细节记录如下：
1) crontab里面的python脚本当中的os.system里面的命令必须写全，如/sbin/bash这样，否则会找不动命令
2) 和这个prefix值，取的时候确实相当啰嗦，本质上还是因为没有一个简单一点的命令，另外记住这里的interface的值是写死了的
3) 这里需要注意多台物理机器的话，需要变更n这个值，这个应该抽象到全局配置里面去的，这里使用了一个辅助库subnet-utils
4) 同上
5) 没什么可说的，就是sleep(5)，这里使用了python的json库
6) ndp这个邻居发现协议，是很惊喜的，一开始我选用了之前ipv4一样的方案，在路由器上做静态路由，但是后来发现和v4的行为不一样，v6做了静态路由之后，确实可以正确得从外网访问，但是内网却不行了。另外想了想也不对，因为v6的地址本身都是动态的，所以我配置的不是一个私网地址，而这个地址，也是会变化的，也就是说，每次路由器重启或者租约过期的时候，这条静态路由就失效了。那还有什么意义？
结果发现了之前误解了ndp的意思，其实一个韩国人的文章里也提到了RA，但最后还是用的是ndp，这个协议是值得细细挖掘的，它的confg文件的意思其实和静态路由是一样的，就是对外声明了一件事，这个docker0网段上的东西，我负责，这个很方便，确实的。
这里使用了官方的fileinput库，很好用
7) 这里使用了systemdctl 来控制，这个新机制很友好，比之前的
8) CloudFlare这个库，还挺健壮的，这个就不多说了，还有docker的官方的python库获取容器基础信息

使用了venv的技巧，都在root用户下

	mkdir ~/.venvs
	mkdir ~/.venvs/docker

	python3 -m venv ~/.venvs/docker
	source ~/.venvs/docker/bin/activate

参考资料以及繁琐的实验过程可以参考，README_physics_host.md和READEME_ip_v6.md，以及README_ddns.md

### 安装

谈不上安装，这个脚本运行于/etc/dhcp之下，还有一个文本文件需要提前建立好，venv以及依赖需要提前pip好

二进制依赖主要有crontab，对应的fedora36的包，ndppd的安装，因为没有依赖dhcpclient，所以，那个东西其实不依赖

ip命令这些基础的网络包就不在说，ip 、ifconfig、netstat、route，这几个就不多说了

### SSL证书
certbot-dns-cloudflare.md
我使用了certbot+cloudflare的组合来生成全域名的证书，很方面，参考上面的的说明文件
