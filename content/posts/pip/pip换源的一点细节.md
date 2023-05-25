---
title: "pip 换源的一点细节"
date: 2023-03-28T17:14:00+08:00
draft: true
tags: ["pip", "Python"]
categories: ["各种配置"]
---

## pip config set
自动创建配置文件，更多参数请看：[pip documentation v23.0.1](https://pip.pypa.io/en/stable/cli/pip/)。

```ini
pip config set global.trusted-host pypi.tuna.tsinghua.edu.cnsimple
pip config set global.index-url https://pypi.tuna.tsinghua.educn/  simple
pip config set global.timeout 600
pip config set global.cache-dir D:\pip-cache
```

## --extra-index-url 问题
如果 global config 设置了清华源，然后有一份 requirements.txt 如下

```txt
requests
fastapi
torch --extra-index-url https://download.pytorch.org/whl/cu117
torchvision --extra-index-url https://download.pytorch.org/whl/cu117
torchaudio --extra-index-url https://download.pytorch.org/whl/cu117
```

直接 `pip install -r requirements.txt` 会从清华源下载 CPU 版本的 Torch， `--extra-index-url` 并未生效。
![](https://s2.loli.net/2023/03/28/zgQuYkLTerpwAqd.png)


因此要改成如下形式
```txt
requests
fastapi

--extra-index-url https://download.pytorch.org/whl/cu117
torch
torchvision
torchaudio
```

![](https://s2.loli.net/2023/03/28/VCAkXNIvOafcMDJ.png)
