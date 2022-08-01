certbot-dns-cloudflare

https://zhangshuqiao.org/2021-12/Certbot%E7%94%B3%E8%AF%B7%E6%B3%9B%E5%9F%9F%E5%90%8D%E8%AF%81%E4%B9%A6/

https://certbot-dns-cloudflare.readthedocs.io/en/stable/index.html



### 安装一个虚拟环境
mkdir ~/.venvs
mkdir ~/.venvs/cloudflare

python3 -m venv ~/.venvs/cloudflare
source ~/.venvs/cloudflare/bin/activate

### 安装依赖
pip3 install certbot certbot-dns-


### API TOKEN
在右上角，profile里面，左边API，生成EDIT的token

### 生成
/etc/cloudflare

echo "dns_cloudflare_api_token=zzzzzzzz" > /etc/cloudflare/cloudflare.ini
chmod 0600 /etc/cloudflare/cloudflare.ini

* certbot certonly --email lemonhall2012@qq.com --dns-cloudflare --dns-cloudflare-credentials /etc//cloudflare/cloudflare.ini -d lemonhall.me,*.lemonhall.me


	(cloudflare) [root@fedora36-macbook cloudflare]# certbot certonly --email lemonhall2012@qq.com --dns-cloudflare --dns-cloudflare-credentials /etc//cloudflare/cloudflare.ini -d lemonhall.me,*.lemonhall.me
	Saving debug log to /var/log/letsencrypt/letsencrypt.log
	Requesting a certificate for lemonhall.me and *.lemonhall.me
	Waiting 10 seconds for DNS changes to propagate

	Successfully received certificate.
	Certificate is saved at: /etc/letsencrypt/live/lemonhall.me/fullchain.pem
	Key is saved at:         /etc/letsencrypt/live/lemonhall.me/privkey.pem
	This certificate expires on 2022-10-29.
	These files will be updated when the certificate renews.

	NEXT STEPS:
	- The certificate will need to be renewed before it expires. Certbot can automatically renew the certificate in the background, but you may need to take steps to enable that functionality. See https://certbot.org/renewal-setup for instructions.

	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	If you like Certbot, please consider supporting our work by:
	 * Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
	 * Donating to EFF:                    https://eff.org/donate-le
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	(cloudflare) [root@fedora36-macbook cloudflare]#

### renew
到时候再说

### 安装啊

关键是

https://docs.portainer.io/advanced/ssl

官方文档，看一下

需要用的其实就这俩
`privkey.pem`  : the private key for your certificate.
`fullchain.pem`: the certificate file used in most server software.


/etc/letsencrypt/live/lemonhall.me

docker run -d -p 9443:9443 -p 8000:8000 \
    --name portainer --restart always \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v portainer-data:/data \
    -v /etc/letsencrypt/live/lemonhall.me:/certs/live/lemonhall.me:ro \
    -v /etc/letsencrypt/archive/lemonhall.me:/certs/archive/lemonhall.me:ro \
    portainer/portainer-ce:latest \
    --sslcert /certs/live/lemonhall.me/fullchain.pem \
    --sslkey /certs/live/lemonhall.me/privkey.pem

舒畅~~

SSL证书安装好了以后，不是一般的舒畅。。。。,游览器也开始记录密码了，然后再也不弹出恼人的安全提醒了

