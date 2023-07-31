---
title: "WARP 作为科学上网备用手段"
date: "2022-08-11T11:11:20+08:00"
tags: ["warp", "zerotrust", "wireguard", "clash", "raspberry"]
categories: ["各种配置"]
---

## 梯子爆炸
前几天经历过一次两个机场同时失效的情况，期间拿 Cloudflare WARP 客户端暂时顶过去。

**梯子这东西日常使用感受不到好处，一旦所有梯子同时失效只能用灾难来形容。**

虽然 Cloudflare 早几年被玩坏了，但是作为一个备用手段绰绰有余。

## APP 端 ZeroTrust 验证失败的绕过方法
在 Issue 区看到 AndroidStudio 抓包获取 Teams ID 的方法，尝试了一遍发现没什么必要：手动配置更快。

但手机端在验证的最后一步提示失败，挂梯子也无法解决。
![验证 ZeroTrust 失败](https://s2.loli.net/2023/01/21/tuR5ybsF3PEUlVh.jpg)

在 Windows 留意到有一个 DOH 网关的字样。虽然 `warp-cli set-gateway` 是制定官方服务器作 DNS 查询，填到手机上却自动激活了 ZeroTrust。
![dns-gatewary](https://s2.loli.net/2023/01/21/9Swy6TjzQ1PiAMH.png)

![填写子域](https://s2.loli.net/2023/01/21/GnOL1PICqo8hADs.png)

![开启ZeroTrust成功](https://s2.loli.net/2023/01/21/GeFWK3NdLIHszoT.jpg)

## WRAP
配置 ZeroTrust 的教程一搜就有：[滥用 Cloudflare ZeroTrust WARP 科学上网](https://y4er.com/posts/cloudflare-zerotrust-proxy)。

安装好 Cloudflare Windows Desktop Client 后开启本地代理，往 Clash 添加一个 Socks5 服务器即可。

![warp 设置本地代理1](https://s2.loli.net/2023/01/21/qHZ8YnXlgbWGMSK.png)

![warp 设置本地代理2](https://s2.loli.net/2023/01/21/aIxeQyOJMZHp2bS.png)


## Clash
```yaml
mixed-port: 7890

# Linux 和 macOS 的 redir 代理端口
redir-port: 7892

# 允许局域网的连接
allow-lan: true

# 规则模式：Rule（规则） / Global（全局代理）/ Direct（全局直连）
mode: rule

# 设置日志输出级别 (默认级别：silent，即不输出任何内容，以避免因日志内容过大而导致程序内存溢出）。
# 5 个级别：silent / info / warning / error / debug。级别越高日志输出量越大，越倾向于调试，若需要请自行开启。
log-level: info
# Clash 的 RESTful API
external-controller: '0.0.0.0:9090'

# RESTful API 的口令
secret: ''

dns:
  enable: true
  ipv6: true
  listen: '0.0.0.0:53'
  use-hosts: true
  enhanced-mode: fake-ip
  fake-ip-range: 198.18.0.1/16
  nameserver:
    - https://doh.pub/dns-query
    - https://dns.alidns.com/dns-query
  fallback:
    - https://1.0.0.1/dns-query
    - https://45.11.45.11/dns-query
  fallback-filter:
    geoip: true
    ipcidr:
      - 240.0.0.0/4

proxies:
  - name: "WARP+"
    type: socks5
    server: 127.0.0.1
    port: 40000

proxy-groups:
  - name: "手动选择节点"
    type: select
    proxies:
      - "WARP+"

rule-providers:
  reject:
    type: http
    behavior: domain
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/reject.txt"
    path: ./ruleset/reject.yaml
    interval: 86400

  icloud:
    type: http
    behavior: domain
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/icloud.txt"
    path: ./ruleset/icloud.yaml
    interval: 86400

  apple:
    type: http
    behavior: domain
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/apple.txt"
    path: ./ruleset/apple.yaml
    interval: 86400

  google:
    type: http
    behavior: domain
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/google.txt"
    path: ./ruleset/google.yaml
    interval: 86400

  proxy:
    type: http
    behavior: domain
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/proxy.txt"
    path: ./ruleset/proxy.yaml
    interval: 86400

  direct:
    type: http
    behavior: domain
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/direct.txt"
    path: ./ruleset/direct.yaml
    interval: 86400

  private:
    type: http
    behavior: domain
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/private.txt"
    path: ./ruleset/private.yaml
    interval: 86400

  telegramcidr:
    type: http
    behavior: ipcidr
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/telegramcidr.txt"
    path: ./ruleset/telegramcidr.yaml
    interval: 86400

  cncidr:
    type: http
    behavior: ipcidr
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/cncidr.txt"
    path: ./ruleset/cncidr.yaml
    interval: 86400

  lancidr:
    type: http
    behavior: ipcidr
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/lancidr.txt"
    path: ./ruleset/lancidr.yaml
    interval: 86400

rules:
 # 这些是自定义规则，想要的可以继续加。
 - DOMAIN-SUFFIX,cloudflareclient.com,DIRECT
 # 下面的规则是通过上面的rule-provider来确定的
 - RULE-SET,private,DIRECT
 - RULE-SET,reject,REJECT
 - RULE-SET,icloud,DIRECT
 - RULE-SET,apple,DIRECT
 - RULE-SET,google,DIRECT
 - RULE-SET,proxy,WARP+
 - RULE-SET,direct,DIRECT
 - RULE-SET,lancidr,DIRECT
 - RULE-SET,cncidr,DIRECT
 - RULE-SET,telegramcidr,WARP+
 - GEOIP,,DIRECT
 - GEOIP,CN,DIRECT
 - MATCH,WARP+
```

## 待解决的问题
1. ZeroTrust 能提供 50 设备同时在线且不限流量使用，WARP free 与 WARP+ 使用起来也无任何区别，但未来策略是否收紧不好说。
2. WARP Client 会根据最近的地理位置选择连接机房（SJC），有些机房（HKG）虽然能连上但是不稳定，甚至完全连不上。
3. WARP Linux Client 不支持 ARM 平台，树莓派要走 Wireguard。


![不支持 ARM 平台](https://s2.loli.net/2023/01/21/jDxpLyol6iJfKzw.png)

### 复制 23PB 流量 bug
<!-- 刷流量推荐用这个：[warpplus](https://github.com/Oreomeow/warpplus)
![warpplus-telegram-bot](https://s2.loli.net/2023/01/21/PtA9TJbpf5EvhkI.png) -->

什么年代了还在传统[刷推荐流量](https://github.com/Oreomeow/warpplus)，直接 [generatewarpplusbot](t.me/generatewarpplusbot) 生成一个用不完的 key，或者用以下复制 bug。

    备份自己的 key
    到 t.me/warpplus 拷贝一个 23PB 的 key
    手机更换密钥后可用流量变成 23PB，再切换回自己的 key 会发现 23PB 流量已复制到自己账号下

![](https://s2.loli.net/2023/05/24/ewf1AKzPtVp3gkO.png)

### warp-cli
一开始搜`切换warp机房`得不到有效信息，后面找的 [WARP-PLUS-HKG](https://github.com/Windla/WARP-PLUS-HKG) 也不好用。

后面在[官方文档](https://blog.cloudflare.com/announcing-warp-for-linux-and-proxy-mode/)找到相关命令：`set-custom-endpoint`

![warp-cli-help](https://s2.loli.net/2023/01/21/zBqGoNEM8damrQh.png)

这里我犯了一个错误，将 **优选 IP** 和 **endpoint IP** 弄混了。

```bash
warp-cli set-custom-endpoint 优选IP
# 会报如下错误
Error: "Failed to remove Trusted SSID because the SSID was invalid."
```
当时还疑惑优选IP:80|443 端口怎么连不上，后面在 [Issue](https://github.com/fscarmen/warp/issues/101) 才了解到 endpoint 域名是这个：
```code
endgate.cloudflareclient.com:2408
```

广州电信在 `162.159.192.0` 段直连完全连不上，换成 `162.159.193.0` 即可。

![连接延迟](https://s2.loli.net/2023/01/21/LYBz7JNeI9Q6WcO.png)

![测速](https://s2.loli.net/2023/01/21/dRy7fcCsSZ9uTlx.png)

### wireproxy
顺着 [fscarmen/warp](https://github.com/fscarmen/warp) 找到 [wgcf](https://github.com/ViRb3/wgcf/)，导出配置文件后修改 Endpoint 即可用 Wireguard 连上 WARP。

早期还有批处理改系统路由表分流后利用 Wireguard 科学上网的玩法，后面应对 UDP Qos 还套 fake-tcp，都太 Tricky 了。

直接替换相应 Endpoint。

```conf
[Interface]
PrivateKey =
Address = 172.16.0.2/32
Address = 2606:4700:110:8d72:9f99:8ebb:2ebe:8fb9/128
DNS = 1.1.1.1
[Peer]
PublicKey =
AllowedIPs = 0.0.0.0/0
AllowedIPs = ::/0
Endpoint = 162.159.193.1:2408 #engage.cloudflareclient.com:2408
```

在树莓派配置 [warp-go.sh](https://github.com/fscarmen/warp/blob/main/warp-go.sh) 失败后找到 [wireproxy](https://github.com/octeep/wireproxy)，开启本地代理仅需以下配置：
```conf
[Interface]
Address = 172.16.0.2/32
PrivateKey =
DNS = 119.29.29.29,8.8.8.8,1.1.1.1,45.11.45.11

[Peer]
PublicKey =
Endpoint = 162.159.193.1:2408
PersistentKeepalive = 25

[Socks5]
BindAddress = 127.0.0.1:40000
```

但是这种方法挂个后台+自启动也不优雅，将上面的 BindAddress 改为监听 `0.0.0.0` 即可用 Clash 串联树莓派，作为备用手段不要求速度和延迟。

Windows 端启动后隐藏窗口的批处理文件写法，只能在任务管理器找到 `wireproxy.exe` 进程。
```bat
@echo off
if "%1"=="h" goto begin
start mshta vbscript:createobject("wscript.shell").run("""%~nx0"" h",0)(window.close)&&exit
:begin
taskkill /T /F /IM wireproxy.exe
wireproxy.exe -c wireproxy.conf
pause
```

只想 cmd 窗口最小化则可以这么写
```bat
@echo off
taskkill /T /F /IM wireproxy.exe
start /min wireproxy.exe -c wireproxy.conf
```


## 全自动优选 Endpoint
不考虑速度，只测试连通性后根据最低延迟优选 Endpoing，半小时跑一遍脚本


      * */30 * * * /usr/bin/python /home/pi/best_endpiont.py


脚本看注释就能懂，工作普遍用第三方库（方便好用）导致写脚本的习惯不太好，以后尽量改成标准库。

```python
#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import re
import random
import functools
import subprocess
from os.path import abspath, dirname, join
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from loguru import logger

# 进程 Process 的创建远远大于线程 Thread 创建占用的资源
MAX_WORKERS = 10
LATENCY = {}
NODES = [192, 193, 195]  # 有些地区 192 段可能会被墙
REQUEST_TIMEOUT = 3
URL = "https://1.1.1.1/cdn-cgi/trace"
IP_REG = r"Endpoint = (.*?):2408"
BINDADDRESS_REG = r"BindAddress = 0\.0\.0\.0:\d+"
DIR_DIR = abspath(dirname(__file__))
BASECONF = """
[Interface]
PrivateKey = kPRKd3QemCiu3NRISPuxkYulex5Pvm91Yz+Sm5R5bFI=
Address = 172.16.0.2/32
DNS = 1.1.1.1
MTU = 1380

[Peer]
PublicKey = bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo=
AllowedIPs = 0.0.0.0/0
AllowedIPs = ::/0
Endpoint = 162.159.192.1:2408

[Socks5]
BindAddress = 0.0.0.0:19000
"""


def get_best_endpoint(mg_dict) -> str:
    best_endpoint = sorted(mg_dict.items(), key=lambda x: x[1])[0]  # asc
    return best_endpoint


def generate_endpoint_configs() -> list:
    """以随机端口生成各个 IP 段的 wireproxy 配置信息"""
    endpoint_configs = []
    for node in NODES:
        for i in range(1, 11):
            port = random.choice(range(10000, 20000))
            socks_port = re.sub(BINDADDRESS_REG, f"BindAddress = 0.0.0.0:{port}", BASECONF)
            data = re.sub(r"162\.159\.(.*?):2408", f"162.159.{node}.{i}:2408", socks_port)
            endpoint_configs.append(data)
            # 生成文件
            ip = re.findall(IP_REG, data)[0]
            with open(join(DIR_DIR, f"config/{ip}.conf"), "w") as f:
                f.write(data)
    return endpoint_configs


def check_latency(config, mg_dict, mg_lock):
    """
    从生成的配置文件获取 IP 和 PORT
    IP 作为文件名生成多个配置文件，避免同一文件读写冲突
    Port 作为对应代理端口
    """
    ip = re.findall(IP_REG, config)[0]
    port = re.findall(BINDADDRESS_REG, config)[0].split(":")[1]  # ["0.0.0.0", 19000]
    dynamic_proxies = {"http": f"socks5://127.0.0.1:{port}", "https": f"socks5://127.0.0.1:{port}"}
    try:
        wireproxy = subprocess.Popen(args=[f"/home/pi/bin/wireproxy -d -c {DIR_DIR}/config/{ip}.conf"],
                                     shell=True,
                                     stderr=subprocess.PIPE,
                                     stdout=subprocess.PIPE)
        ## stdout.read() 会阻塞
        # logger.error(f"os.getpid() -> stdout:{wireproxy.stdout.read()}")
        # logger.error(f"os.getpid() -> stderr:{wireproxy.stderr.read()}")
        res = requests.get(url=URL, proxies=dynamic_proxies, timeout=REQUEST_TIMEOUT)
        if res.status_code == 200:
            logger.info(f"ip: {ip}, elapsed: {res.elapsed.total_seconds()}")
            with mg_lock:
                mg_dict[ip] = res.elapsed.total_seconds()
    except Exception as e:
        logger.error(f"ip: {ip}, Exception: {str(e)}")
        with mg_lock:
            mg_dict[ip] = 999
    finally:
        wireproxy.kill()


def rewrite_restart(best_endpoint):
    """覆写本地配置文件再重启服务"""
    global BASECONF
    # wireproxy 配置默认 19000 端口，串联 Clash
    base = re.sub(r"Port = \d+", f"Port = 19000", BASECONF)
    bind_address = re.sub(BINDADDRESS_REG, f"BindAddress = 0.0.0.0:19000", base)
    ip = best_endpoint[0]
    config = re.sub(r"Endpoint = (.*?):2408", f"Endpoint = {ip}:2408", bind_address)
    with open("/home/pi/config/wireproxy.conf", "w") as f:
        f.write(config)
    subprocess.run(args=["sudo killall wireproxy"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(args=["/home/pi/bin/wireproxy -d -c /home/pi/config/wireproxy.conf"],
                   shell=True,
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE)


if __name__ == "__main__":
    # windows 在头部引用会触发 spwan error，还需要 freeze_support()
    from multiprocessing import Manager  # 多进程，大量子进程由 Pool 维护，少量子进程用 Process 比较灵活
    # 多进程共享变量
    mg_dict = Manager().dict()  # {ip: latency, ip2: latency2...}
    mg_lock = Manager().Lock()
    # 多进程封装多变量
    pt = functools.partial(check_latency, mg_dict=mg_dict, mg_lock=mg_lock)
    # 生成配置文件
    endpoint_configs = generate_endpoint_configs()
    # 多线程池
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(pt, endpoint_configs)
    # 输出结果
    best_endpoint = get_best_endpoint(mg_dict)
    logger.add(f"{DIR_DIR}/run.log", format="{time} {level} {message}")
    logger.debug(f"best_endpoint: {best_endpoint}")
    # 重启服务
    rewrite_restart(best_endpoint)

```


至此，一个能用的科学上网备用手段就完全配置好了。
