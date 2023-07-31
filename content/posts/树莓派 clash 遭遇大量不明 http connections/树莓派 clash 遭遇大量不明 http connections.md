---
title: 树莓派 clash 遭遇大量不明 http connections
date: 2023-07-28T01:30:54+08:00
draft: false
tags: ["clash", "树莓派"]
categories: ["树莓派"]
---

今晚登录树莓派发现输入延迟很高，`htop` 打开一看 clash 占用的内存快拉满了，`netstat -anp` 发现有很多不明连接。

搜到相关 Issue：[请考虑关闭 Allow-Lan](https://github.com/Fndroid/clash_for_windows_pkg/issues/2769)，还是那句：任何需要部署到公网的东西都要注意权限（身份验证+端口限制）最小化。

```yaml
allow-lan: true
authentication:
  - "<user>:<pass>"
external-controller: '127.0.0.1:9090'
secret: '<secret>'
```

还好在树莓派上跑的是备用代理 CloudFlare WARP，要是机场梯子的话 200G 流量一下午就能刷完。

添加相应配置之后就没有不明 IP 连进来了。  
![](https://s2.loli.net/2023/07/28/FHgZBYo5rDvciMz.png)


