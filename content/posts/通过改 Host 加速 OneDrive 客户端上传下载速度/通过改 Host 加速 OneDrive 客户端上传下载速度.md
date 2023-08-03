---
title: 通过改 Host 加速 OneDrive 客户端上传下载速度
date: 2023-08-03T11:24:33+08:00
draft: false
tags: ["onedrive", "host", "UsbEAm Hosts Editor"]
categories: ["onedrive"]
---

OneDrive 在绝大部分地区只要能登陆上（登录域名被墙）还是能同步的，同步速度根据当地情况而定。

## 直连配置
但是 OneDrive 同步大文件一不留意就耗费梯子大量流量，所以根据官网：[OneDrive 所需的 URL 及端口](https://learn.microsoft.com/zh-cn/sharepoint/required-urls-and-ports)维护了一份 [OneDrive 直连域名列表](https://raw.githubusercontent.com/eve2ptp/clash-custom-list/main/clash_onedrive_direct.txt)。相关登录域名依旧走代理，直连域名只作用于客户端上传/下载，可以根据 Clash 连接情况修改。
```shell
payload:
  - 'onedrive.com'
  - 'onedrive.live.com'
 # - 'login.live.com'
  - 'g.live.com'
  - 'spoprod-a.akamaihd.net'
  - 'p.sfx.ms'
  - 'oneclient.sfx.ms'
  - 'fabric.io'
  - 'vortex.data.microsoft.com'
  - 'posarprodcssservice.accesscontrol.windows.net'
  - 'redemptionservices.accesscontrol.windows.net'
  - 'token.cp.microsoft.com/'
  - 'tokensit.cp.microsoft-tst.com/'
  - 'vas.samsungapps.com'
  - 'odc.officeapps.live.com'
 # - 'login.windows.net'
  #- 'login.microsoftonline.com'
  - 'storage.live.com'
  - 'favorites.live.com'
  #- 'oauth.live.com'
  - 'photos.live.com'
  - 'skydrive.live.com'
  #- 'api.live.net'
  #- 'apis.live.net'
  - 'docs.live.net'
  - 'policies.live.net'
  - 'settings.live.net'
  - 'skyapi.live.net'
  - 'snapi.live.net'
  - 'storage.msn.com'
  - '+.onedrive.com'
  - '+.mesh.com'
  - '+.microsoft.com'
  - '+.crashlytics.com'
  - '+.office.com'
  - '+.officeapps.live.com'
  - '+.aria.microsoft.com'
  - '+.mobileengagement.windows.net'
  - '+.branch.io'
  - '+.adjust.com'
  - '+.servicebus.windows.net'
  - '+.files.1drv.com'
  - '+.onedrive.live.com'
  - '+.storage.live.com'
  - '+.groups.office.live.com'
  - '+.groups.photos.live.com'
  - '+.groups.skydrive.live.com'
  - '+.docs.live.net'
  - '+.policies.live.net'
  - '+.settings.live.net'
  - '+.livefilestore.com'
  - '+.storage.msn.com'
```

Clash 的配置：
```yaml
rule-providers:
  onedrive_direct:
    type: http
    behavior: domain
    url: https://raw.githubusercontent.com/eve2ptp/clash-custom-list/main/clash_onedrive_direct.txt
    path: ./ruleset/onedrive_direct.yaml
    interval: 86400
   
rules:
 - RULE-SET,onedrive_direct,DIRECT
```

## 提速
如果直连速度理想那么到这就结束了。但是很遗憾，不改 host 的情况下只有 100~300k 的速度甚至连不上。  
![](https://s2.loli.net/2023/08/03/5Ji1Bv2lZoTUuAn.png)

[UsbEAm Hosts Editor](https://www.dogfight360.com/blog/475/) 就没啥好说的了，直接改 host 看看效果。
![](https://s2.loli.net/2023/08/03/V3psOt9N26zYo7l.png)

![](https://s2.loli.net/2023/08/03/mDeho6Z8JTB7CXt.png)

再加一行在使用的域名。
![](https://s2.loli.net/2023/08/03/GaeS3Z1FXwtDT7r.png)

效果拔群，惊了。
![](https://s2.loli.net/2023/08/03/Rs91M85FUvd4qhQ.png)

![](https://s2.loli.net/2023/08/03/zbfYBOtDAvEVXFM.png)