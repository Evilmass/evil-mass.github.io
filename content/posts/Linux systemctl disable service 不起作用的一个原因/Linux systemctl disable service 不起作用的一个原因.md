---
title: Linux systemctl disable service 不起作用的一个原因
date: 2023-07-31T20:19:08+08:00
draft: false
tags: ["linux", "树莓派"]
categories: ["linux"]
---

即便是删除掉依赖的可执行文件 + `systemctl disable --now vmess.service` 重启，相关僵尸进程也会一直启动。
![](https://s2.loli.net/2023/07/31/Rh6Ys1cKFxerWoL.png)

解决办法：请仔细检查目前在运行的服务配置里面是否存在 `After` 依赖。
```shell
[Unit]
Description=Control Raspberry Pi with Telegram Bot
After=network.target clash

[Install]
WantedBy=multi-user.target

[Service]
Type=simple
WorkingDirectory=/home/pi/sh/raspbot
ExecStart=/home/pi/pyenvs/tgbot/bin/python3 raspbot.py
Restart=always
```
