---
title: "我在树莓派上跑了多少服务"
date: 2023-01-29T17:04:42+08:00
tags: ["Raspberry", "树莓派"]
categories: ["树莓派"]
---


## 你真的需要云服务器吗
大二买的 Raspberry Pi 3B+ 至今服役在家里的路由器旁，虽然我从未拿它做什么正儿八经的研究和生产，但是想要折腾新东西的时候总是先在上面跑。

想起前几年买的国内云学生机，食之无味弃之不可惜。一方面写写博客纯静态页面挂载在 [GitHub](https://github.com) 上足够，另一方面很多用得到的服务也不需要这么多性能。


## fail2Ban
仓库地址：[fail2Ban](https://github.com/fail2ban/fail2ban/wiki/How-to-install-or-upgrade-fail2ban-manually)

![](https://s2.loli.net/2023/01/29/inwGSRNytvZEUxQ.jpg)

如果用的是 `Python3`，需要先执行一遍 `./fail2ban-2to3`。不然会报如下错误：
```shell
ERROR: No module named 'ConfigParser'
```


## aliddns
仓库地址：[aliddns](https://github.com/OpenIoTHub/aliddns)

![](https://s2.loli.net/2023/01/29/BzehY8rCPJwsjZu.png)

广州电信给了公网 IPV4 地址，路由器也开启了相应 ddns 以及端口映射。树莓派的 ddns 主要是解析 IPV6 地址，多点保险手段总是好的。


## UnblockNeteaseMusic
仓库地址：[UnblockNeteaseMusic](https://github.com/nondanee/UnblockNeteaseMusic)

![](https://s2.loli.net/2023/01/29/rFsUO5Y4iAMv96f.png)


## Clash
仓库地址：[Clash](https://github.com/Dreamacro/clash)

![](https://s2.loli.net/2023/01/29/32QGty4mVhWBaFD.png)

自用机场和 WARP(wireproxy) 两套配置，后者反而还稳定些（低频率请求）。


## go-cqhttp
仓库地址：[go-cqhttp](https://github.com/Mrs4s/go-cqhttp)

![](https://s2.loli.net/2023/01/29/sOn2edavQUtXJMh.png)

配合 nonebot 插件跑 qq 机器人，平时搜搜图还是很好用的。


## v2ray
仓库地址：[V2ray](https://github.com/v2fly/v2ray-core)

![](https://s2.loli.net/2023/01/29/PzsdTEh4F2jDXlI.png)

前两年折腾联通 host 免流：直接花三块钱买网上提供的云免流服务，直接把各种 host 保存下来。一不需要手机安装 `PackageCapture` 抓包，二不怕短期失效。

    pull.free.video.10010.com
    shoutingtoutiao1.10010.com

现在公司和家里的 WiFi 覆盖时间已经完全不需要折腾了。工作之后对时间开销看得更重：能花钱解决的中长期（持续需求）问题一律花钱解决。

**当然，国内网盘这种东西不值得我付费。**


## OneDrive
之前也尝试过用[全量备份脚本](https://github.com/nanhantianyi/rpi-backup)然后隔段时间就保存到电脑，但是压缩镜像耗时问题以及反复解压很容易忘记备份了什么。

现在干脆直接将本地目录（常用软件、各类配置文件）整个上传到 `OneDrive`，`crontab` 下加一行实现定时增量备份。
```shell
/home/pi/bin/rclone sync /home/pi/ rasp:/Raspberry --transfers 16 -P --onedrive-chunk-size 40M
```

用到的 `Rclone` 配置看这篇：[Linux使用Rclone挂载OneDrive网盘](https://333rd.net/posts/tech/linux%E4%BD%BF%E7%94%A8rclone%E6%8C%82%E8%BD%BDonedrive%E7%BD%91%E7%9B%98/)


## telegrambot
文档地址：[python-telegram-bot](https://docs.python-telegram-bot.org/en/stable/)

![](https://s2.loli.net/2023/01/29/5vyo1N7m6XetH9j.webp)


在外有电脑远程连回树莓派是挺方便，但是只有手机的情况下敲命令还反复缩放界面看服务运行情况就不太优雅了。

官方给的接口很全，只要你愿意，用 `Flask` 接入都没问题。功能少还是直接写比较快。

参考 [Warpplus](https://github.com/Oreomeow/warpplus)

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import logging
import subprocess
from typing import Optional, Union

from telegram import Update, error
from telegram.ext import CallbackContext, CommandHandler, Updater

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Telegram bot API Token (可在 @botfather 获取)
TOKEN = "TOKEN_HERE"
# Telegram 用户 ID (在 @getidsbot 发送 /start 获取)
USER_ID = "USER_ID_HERE"

class RaspBot(object):
    def __init__(self, user_id: int):
        self._user_id = str(user_id)
        self._bot = None
        self._update = None
        self._message_id = None

    @staticmethod
    def is_who(update: Update, n: Optional[int] = 3) -> tuple:
        chat_id = update.message.chat_id
        user_id = update.message.from_user.id
        username = update.message.from_user.username
        first_name = update.message.from_user.first_name
        name = username if username else first_name
        chat_type = update.message.chat.type
        if n == 6:
            return chat_id, user_id, username, first_name, name, chat_type
        return chat_id, user_id, name

def send_command(update: Update, context: CallbackContext):
    chat_id, user_id, name = RaspBot.is_who(update)
    logging.info(f"{name} ({user_id}) | 正在输入命令...")
    if not context.args:  # 无参数
        result = "no args input"
    else:
        _args = context.args
        result = subprocess.run(" ".join(_args), stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        logging.info(f"command: {_args}")
        logging.info(f"returncode: {result.returncode}")
        logging.info(f"stderr: {result.stderr.decode('utf-8')}")
        logging.info(f"stdout: {result.stdout.decode('utf-8')}")

    # telegram 信息最大长度为 4096 bytes
    if len(result.stdout) >= 4096:
        result.stdout = result.stdout[:4096]

    context.bot.send_message(
        chat_id=chat_id,
        text=f"returncode: {result.returncode}\n"
            +f"stderr: {result.stderr.decode('utf-8')}\n"
            +f"stdout: {result.stdout.decode('utf-8')}\n"
    )

def start(update: Update, context: CallbackContext):
    chat_id, user_id, name = RaspBot.is_who(update)
    logging.info(f"[+] {name} ({user_id}) | 欢迎使用")
    message_id = context.bot.send_message(
        chat_id=chat_id,
        text=f"{name}，欢迎使用\n"
        + "/start - 开始使用\n"
        + "/c - 命令行\n",
        parse_mode="Markdown"
    ).message_id
    del_msg(60, context, chat_id, message_id)

def main():
    updater = Updater(TOKEN, use_context=True, request_kwargs={"proxy_url": "http://127.0.0.1:7890"})  # Updater 设置代理
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start, run_async=True))
    dp.add_handler(CommandHandler("c", send_command, run_async=True))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
```

还有一些签到类（b站直播间、v2ex）脚本就不提了，时效性一般。
