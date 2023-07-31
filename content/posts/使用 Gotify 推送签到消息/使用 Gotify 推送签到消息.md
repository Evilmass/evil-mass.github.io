---
title: 使用 Gotify 推送签到消息
date: 2023-07-25T12:44:41+08:00
draft: false
tags: ["gotify"]
categories: ["工具"]
---

## 选型
目前在 huggingface 部署了多个签到脚本，由于仓库设置成 Private，想看脚本输出就只能在浏览器请求 `log/filename=<filename>&token=<token>` 接口。

及时获取签到通知就成了一个新需求，要求如下：
1. 能自建推送服务器。
2. 足够简单。

> 日志隐私保护可有可无，单纯是数据在自己手上比较安心。  
签到日志输出内容： `<datetime.now> <sign_platform> <sign_result>`，没有任何利用价值。
> 
> 简单则是针对安卓端的需求：安卓推送需要 [FCM](https://firebase.google.com/docs/cloud-messaging)（绑定谷歌三件套）必须在后台一直挂着梯子，所以 App 方案反而是能接受的。

那可选的也就不多了。  
首先排除：WxPusher、Server酱、TelegramBot、QQBot、邮箱。  
还剩下 [pushdeer](https://github.com/easychen/pushdeer)、[Bark](https://github.com/Finb/Bark)、[Gotify](https://github.com/gotify/server)。

## pushdeer
最开始吸引我的是 pushdeer，下载 App 打开后发现 UI 做的还可以。

But
![](https://img.evimo.top/需要微信登录.jpg)

emmm，登录进去发现安卓端还没有开发好自建服务器的功能，推送信息下面还带广告，直接弃用。
![](https://img.evimo.top/pushdeer带广告.jpg)

## Bark
针对 Apple 设备推送的效果很好，但是官方没有提供安卓端的 App，目前只有 [PushLite](https://github.com/xlvecle/PushLite/) 可用，要一直挂着梯子，且 PushLite 界面过于简陋，弃用。

## Gotify
官方文档清晰明了，无论是搭建服务端还是使用客户端接收消息都突出一个简单易用还好用。

**do one thing，and do well.**

### 服务端
树莓派使用可执行文件 + Nginx 做反向代理。
```shell
# > curl -s https://api.github.com/repos/gotify/server/releases/latest | grep "browser_download_url" | grep arm64 | cut -d '"' -f 4
# > https://github.com/gotify/server/releases/download/v2.3.0/gotify-linux-arm64.zip

# 获取最新版本的下载链接，wget -i 表示指定 url 来源，- 表示url来源为 stdin。
mkdir gotify-server
cd gotify-server
curl -s https://api.github.com/repos/gotify/server/releases/latest | grep "browser_download_url" | grep arm64 | cut -d '"' -f 4 | wget -i -
# 解压
unzip gotify*.zip
# 给予可执行权限
chmod +x gotify*
# 获取运行配置文件
wget -O config.yml https://raw.githubusercontent.com/gotify/server/master/config.example.yml
# 修改相应端口为 38000
sed -i s'/80/38000' -i config.yml
# 运行
sudo ./gotify*
```

如果是国内服务器或家庭宽带有公网 IP（封锁 80/443 端口） + 未备案域名，可以先用 [dns challenge](http://ocdman.github.io/2018/08/31/%E6%A0%91%E8%8E%93%E6%B4%BE%E5%AE%89%E8%A3%85letsencrypt%E8%AF%81%E4%B9%A6/) 绕过获得 `gotify.<your_domain>` SSL 证书，然后再使用 [aliddns](https://github.com/OpenIoTHub/aliddns) 定时自动更新 IP 并解析到域名上。
```nginx
# nginx 服务器配置
server {
    listen [::]:80;
    listen [::]:443 ssl http2;
    server_name <your_domain>;  # 解析的域名，自定义替换

    if ($server_port !~ 443){
        rewrite ^(/.*)$ https://$host$1 permanent;
    }

    #SSL配置
    # RSA Cert
    ssl_certificate /etc/letsencrypt/live/<your_domain>/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/<your_domain>/privkey.pem;

    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20
-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384::!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
    # add_header Strict-Transport-Security "max-age=31536000" always;    # HSTS 设置，按需启用

    error_page 497  https://$host$request_uri;

    # . files
    location ~ /\.(?!well-known) {
        deny all;
    }

    # robots.txt
    location = /robots.txt {
        default_type text/html;
        add_header Content-Type "text/plain; charset=UTF-8";
        return 200 "User-Agent: *\nDisallow: /";
    }
    
    # 如果要使用自定义后缀就改 location 的 / 为 /<path>
    location / {
      proxy_pass         http://localhost:38000;
      proxy_http_version 1.1;

      # Ensuring it can use websockets
      proxy_set_header   Upgrade $http_upgrade;
      proxy_set_header   Connection "upgrade";
      proxy_set_header   X-Real-IP $remote_addr;
      proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header   X-Forwarded-Proto http;
      proxy_redirect     http:// $scheme://;

      # The proxy must preserve the host because gotify verifies the host with the origin
      # for WebSocket connections
      proxy_set_header   Host $http_host;

      proxy_connect_timeout   7m;
      proxy_send_timeout      7m;
      proxy_read_timeout      7m;
    }

}
```

重启 nginx 服务器之后就能在 `http://localhost:38000` 看到 Gotify 的网页版了。
第一次进去要重置 admin 密码，然后按需求创建不同的应用来分类，Gotify 会根据不同应用的 `Token` 来推送消息。  
![](https://img.evimo.top/gotify%20create%20app%20token.png)

测试推送
```python
import requests

"""
extras 的 bigImageUrl 参数只能使用直链图片 url，
sm.ms 图床的图片 url 会跳转一次导致无法正常显示。
"""

# gotify 推送
def push_msg(title: str = "无标题", message: str = "无内容", img_url: str = gotify_img):
    url = f"https://{gotify_domain}/message?token={gotify_token}"
    resp = requests.post(
        url=url,
        json={
            "title": title,
            "message": message,
            "priority": 10,
            "extras": {
                "client::display": {"contentType": "text/markdown"},
                "client::notification": {"bigImageUrl": img_url}
            }
        }
    )
    return resp.json()
```
  
![](https://img.evimo.top/gotify发送测试.png)

成功接收消息。  
![](https://img.evimo.top/test-notify.png)

### 客户端
2.7.0 版本加入了自动重连的功能，原因是安卓系统默认针对在后台运行的 App 执行**电池优化**，所以还是建议手动加到白名单。即便如此 Gotify 实际使用下来一天也只耗 2% 的电，几乎忽略不计。

**已经多久没见过只有 5m 的 App 了。**  
![](https://img.evimo.top/客户端大小只有5m，点个赞.png)



填入你的推送域名和登录信息即可。  
![](https://img.evimo.top/gotify-android.png)

带图片的推送。  
![](https://img.evimo.top/gotify-android-test.jpg)