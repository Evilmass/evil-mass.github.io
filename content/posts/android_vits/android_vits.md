---
title: "使用安卓设备运行 vits 语音合成"
date: 2023-03-18T13:13:33+08:00
tags: ["vits", "ai语音合成", "UserLAnd", "Termux", "Nubia Z9", "LinuxDeploy", "pyopenjtalk"]
categories: ["vits"]
---

配置不难就是坑多，而且**完全不可用**。

## PRoot 与 chroot
chroot 和 PRoot的一个主要区别是 chroot 是原生的。

    PRoot通过使用 ptrace() 劫持系统调用参数和返回值来伪造文件系统布局和用户/组ID。
    chroot不造成额外的开销，在任何设备上都不会出现问题，但是它需要root权限。

所以基于PRoot的 [UserLAnd](https://github.com/CypherpunkArmory/UserLAnd/releases) 和 [Termux](https://github.com/termux/termux-app/releases) 并不适合。
一开始用 UserLAnd 配置环境倒是没问题，但是执行到 `pip install package` 的时候就报 `Permission Denied` 错误。


## root
闲置机器是 [Nubia Z9](https://detail.zol.com.cn/picture_index_1524/index15235004_0_p391967.shtml#/&pn=177)，安卓 5.2 版本直接线刷回出厂版本后使用 [Kingroot](https://kingrootapp.net/) 一键 root。

不得不说这块屏幕和金属边框设计放到 2023 年还是很漂亮，最近新出的 [Z50 Ultra](https://www.ztedevices.com/cn/product/nubia-z50-ultra/) 也是类似设计。
![](https://s2.loli.net/2023/03/18/9G1w6TdSDEiYWfK.png)

可惜的是 骁龙810 + 电池 2900毫安 + 3G 运行内存。810 在日常室温使用只能用**烫手**来形容，加上扎实的手感，拿起来怕摔加保护壳又没手感+升温，当日常备用机完全不合适。


## LinuxDeploy
仓库地址：[LinuxDeploy](https://github.com/meefik/linuxdeploy/releases)

基本按图里面的配置或者全程科学上网都没有什么问题，[BusyBox](https://github.com/meefik/busybox/releases) 实测是不需要的。

架构选 ARM64 即可，系统一定要选 LTS Release，[非 LTS 不支持 deadsnakes 源](https://github.com/deadsnakes/issues/issues/142#issuecomment-790081078)，`apt get install python3.7` 肯定比源码编译快多了。当然，想尝试花一个小时从源码编译 Python3.7 我也不拦着（


### 坑1：系统版本
[Ubuntu 16.04.7 LTS (Xenial Xerus)](https://releases.ubuntu.com/16.04/) 默认 Python3.5 安装 [pytorch](https://pytorch.org/get-started/locally/) 会报错。

[Ubuntu 22.04.2 LTS (Jammy Jellyfish)](https://releases.ubuntu.com/jammy/) 的 Python3.10 则有依赖问题。


### 坑2：extract/ssh start failed
一开始想自动分配空间，安装类型选了`目录`而不是`镜像文件`。

全程科学上网或换国内源安装均会报错，开 debug 提示 `/bin/su no such file or directory`。
![](https://s2.loli.net/2023/03/18/24b8aEzWZgwoixS.png)

没找到好的解决方法，如果可以目录安装还是建议用目录，镜像分配空间不管大小都不是很合适。


### 坑3：默认分配的镜像大小是 2G
你可以想象一下**编译了一个小时的 Python3.7** + **安装依赖不报错**的情况下，突然提示空间分配不足且**找不到扩容方法**的心情吗。


### 部署
基本按照图里的设置就能成功部署起来了，填写国内镜像源，勾选 SSH 服务，挂载点、声音、图形都不需要。
![](https://s2.loli.net/2023/03/18/UoR7mEJ1CjQ8IXK.png)
![](https://s2.loli.net/2023/03/18/FlDEUkvWC3wyPBm.png)
![](https://s2.loli.net/2023/03/18/gBNGJRO8eUCbqYD.png)
![](https://s2.loli.net/2023/03/18/Z6wqvaVS9x8l2NA.png)
![](https://s2.loli.net/2023/03/18/XgWl7u5NvQILzmw.png)


#### 从 dash 切换到 bash
启动成功之后 SSH 连进去即可。
运行下面代码 选 no 重新进终端即可。
```bash
sudo dpkg-reconfigure dash
```
![](https://s2.loli.net/2023/03/18/n3Eb8qieZ6pUHhx.png)



```bash
# 更换国内源
sudo cp /etc/apt/source.list /etc/apt/source.list_bak
vim /etc/apt/source.list

deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ bionic main restricted universe multiverse
deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ bionic-updates main restricted universe multiverse
deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ bionic-backports main restricted universe multiverse
deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ bionic-security main restricted universe multiverse
# 基础软件
sudo apt update
sudo apt install wget curl vim git screen build-essential
```

#### 安装 Python3.7 & pip
`No module named 'distutils.util` 报错是因为没安装 `python3.7-distutils`。

`error: command ‘/usr/bin/aarch64-linux-gnu-gcc’ failed with exit code 1` 报错是因为没安装 `python3.7-dev`。

```bash
# !deadsnakes is only for ubuntu LTS releases!
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get install python3.7 python3.7-distutils python3.7-dev
curl https://bootstrap.pypa.io/get-pip.py | python3.7
```

#### 坑4：不要使用国内 pip 源
安装 `pyopenjtalk` 和其他依赖会报 `403` 错误。


#### 配置虚拟环境
```bash
/home/pi/.local/bin/pip3.7 install virtualenv
python3.7 -m virtualenv venv
source venv/bin/activate
```

#### vits
提供局域网内一个 Clash 的代理，如果直连 pypi 官方源速度很快则不需要。

```bash
export http_proxy="http://192.168.1.162:7890"
export https_proxy="http://192.168.1.162:7890"
```

修改 `requirements.txt`，三个 torch 后面的 --extra-index-url 都去掉（使用 CPU 推理）。

只做推理不需要`demucs`、`openai-whisper`、`gradio`，再加上 `fastapi`、`uvicorn`、`loguru`。

```git
git clone https://ghproxy.com/https://github.com/Plachtaa/VITS-fast-fine-tuning
pip install -r requirements.txt
```

`api.py` 和 `server.py` 参考 [vits-mandarin-windows](https://github.com/rotten-work/vits-mandarin-windows) 即可。

只能说这个推理速度完全不意外，又是折腾没结果的一天。
![](https://s2.loli.net/2023/03/18/wHx5jFCMVglO8dn.png)

## 2023 年两台手机用蓝牙传图有种时代落幕感
![](https://s2.loli.net/2023/03/18/iIaQHxJtqs4S8Lb.jpg)