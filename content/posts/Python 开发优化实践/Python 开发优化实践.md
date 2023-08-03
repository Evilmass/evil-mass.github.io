---
title: Python 开发优化实践
date: 2023-07-31T18:15:39+08:00
draft: false
tags: ["python"]
categories: ["python"]
---

前天推送了一个不错的视频：[【Code Review】传参的时候有这么多细节要考虑？冗余循环变量你也写过么？](https://www.bilibili.com/video/BV1gh4y1y7Rv/)

日常开发中确实在 code review 也会提到视频里的一些点，这里记录一下。

## 传参
接触过 FastAPI 的 Schema Check 应该很熟悉 [TypeHint](https://docs.python.org/3/library/typing.html) 和 [Pydantic](https://docs.pydantic.dev/latest/) 这种写法，尤其是参数校验在实际开发有多直观。说明文档固然重要，但是逻辑清晰、简洁美观的代码更胜一筹。  
```python
from datetime import datetime
from typing import Tuple
from pydantic import BaseModel

class Delivery(BaseModel):
    timestamp: datetime
    dimensions: Tuple[int, int]
```

而反面示例如下：
```python
def process_data(is_checked: bool = False, **kwargs) -> None:
    if is_checked:
        for key, value in kwrags.items():
            # process work

def func(data: dict) -> list:
    res = []
    timestamp = data.get("timestamp")
    refresh = data.get("refresh", False)
    rate = data.get("rate", 0.11)
    push_date = data.get("push_date", "")
    # process work
    return res
```

虽然也有 typehint，传参返回值也有默认处理，但

`process_data` 这个 `**kwargs`  压根不知道从哪传进来，传了什么进来。

`data` 是一个不固定的传参。哪天业务新增传参进来，别的地方引用到这个函数的时候，报错都找不到。

## 变量命名
还是上面的反面例子：
```python
def get_data_list() -> list:
    res = []
    # process work
    return res

result = get_data_list()
for x in result:
    # process work
```

完全没有对应数据处理流程中的任意变量，两个星期回来再看都不知道这函数做了什么。

可读性更好的写法：
```python
def get_ai_precheck_data() -> list:
    ai_precheck_data = []
    # process work
    return ai_precheck_data

ai_precheck_data = get_ai_precheck_data()
for apd in ai_precheck_data:
    # process work
```

## from config import *
生产/开发环境一般都会有 `config_prod | config_dev` 两个配置文件，而配置文件里面又区分明文和非明文。 非明文敏感信心建议从另一台授权机器上获取，开发代码中用 `os.environ.get(value)`。

如果这么写，**.gitignore 一定要添加 config.settings_dev.py**
```python
# 全局变量 DIR_PATH 不能在其他地方用同一个命名，会被替换
import sys
from os.path import abspath, dirname

DEBUG = False
if DEBUG:
    DIR_PATH = abspath(dirname(__file__))
    sys.path.append(DIR_PATH)
    from config.settings_dev import * 
else:
    DIR_PATH = "/home/user/app"
    sys.path.append(DIR_PATH)
    from config.settings_prod import * 

# 在需要变量的文件引入
from __init__ import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASS,
)
```

在模块多且复杂的时候，`config` 文件夹里面应当按业务模块继续划分配置文件以存储相应信息。

## IO & 大文件 & 内存
遇到以上情况一定格外注意**执行效率**和**内存耗尽**问题。

关于执行效率直接抄 [论写代码的合理性](https://www.cnblogs.com/ydf0509/p/13431548.html) 的代码了，反复创建连接-执行 vs 批量处理 vs 池。
```python
from redis import Redis
from decorator_libs import TimerContextManager

# redis://:yMxsueZD9yx0AkfR@192.168.199.202:6543/7
with TimerContextManager():
    for i in range(10000):  # 180s
        r = Redis(host='192.168.199.202', port=6543, password='yMxsueZD9yx0AkfR', db=8)
        r.lpush('a1', 1)

with TimerContextManager():  # 42秒
    r = Redis(host='192.168.199.202', port=6543, password='yMxsueZD9yx0AkfR', db=8)
    for i in range(10000):
        r.lpush('a2', 1)

with TimerContextManager():  # 0.26秒
    r = Redis(host='192.168.199.202', port=6543, password='yMxsueZD9yx0AkfR', db=8)
    with r.pipeline() as p:
        for i in range(10000):
            p.lpush('a3', 1)
        p.execute()
```

第二点则是在开发中遇到处理耗时函数时同时要意识到还有内存问题，几个巨型 `list|tuple|dict` 不触发 GC能把为数不多的服务器内存吃完。