# huggingface 部署 docker 记录


继 [Heroku](http://www.heroku.com/pricing#1-0)、[Railway](https://docs.railway.app/reference/pricing) 收费后，能免费使用（好用）的网站托管服务还剩下 [Vercel](https://vercel.com/pricing)和 [Huggingface](https://huggingface.co/pricing)。  

但 Vercel [不支持 docker deployment](https://vercel.com/guides/does-vercel-support-docker-deployments)，huggingface 限制则很少。

**unlimited！** 
![](https://s2.loli.net/2023/07/27/pxeEh6A8GZ3undT.png)

确实良心。  
![](https://s2.loli.net/2023/07/27/yDJZjIGLWB2hUid.png)

## 配置文件
[官方文档](https://huggingface.co/docs/hub/spaces-sdks-docker)其实很清晰了，这里简单贴一下没有读写权限问题的 FastAPI Server 配置。

### README.md
```shell
---
title: Sig
emoji: 🐢
colorFrom: green
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
```

### Dockerfile
利用[多级构建缓存](https://juejin.cn/post/7113788803914924040#heading-0)减少后续部署时间。
```docker
# build cache
FROM python:3.9-slim-bullseye as builder

WORKDIR /tmp

# depends
RUN apt-get update -y
COPY ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# playwright
RUN playwright install-deps
  
# Set up a new user named "user" with user ID 1000
RUN useradd -m -u 1000 user

# Switch to the "user" user
USER user

# Set home to the user's home directory
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set the working directory to the user's home directory
WORKDIR $HOME/app

# create folder
RUN mkdir $HOME/app/cookie $HOME/app/log $HOME/app/_playwright $HOME/app/config

# Try and run pip command after setting the user with `USER user` to avoid permission issues with Python
RUN playwright install chromium firefox

# use build cache 
FROM builder

# Copy the current directory contents into the container at $HOME/app setting the owner to the user
COPY --chown=user . $HOME/app

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
```

## app.py
必须要有 `app.py` 才能运行服务。
```python
# coding: utf-8
from fastapi import FastAPI
from fastapi.responses import Response

app = FastAPI()


@app.get("/")
def home():
    html_content = open("index.html").read()
    return Response(content=html_content, status_code=200)
```

## 外网连通性
当使用私有域名进行数据交互的时候，无法从容器内发送请求到外部，而本地不同网络下测试是正常的。  
可能是 bug。  
![](https://s2.loli.net/2023/07/27/2ZqrDhpKi9jwFO4.png)

```python
# 成功
requests.get("https://checkip.amazonaws.com").text.strip()
# 失败
requests.get("https://<your_domain>/v1/request").text.strip()
```

目前只能通过 `IP:PORT` 的方式处理数据。  

## Secret
如果要在部署环境使用敏感信息，可以在环境变量添加 `ACCESS_TOKEN` 后在 [[huggingface 部署 docker 环境#Dockerfile]] 加入下面的内容：

```shell
RUN --mount=type=secret,id=ACCESS_TOKEN,mode=0444,required=true \
curl test -H 'Authorization: Bearer $(cat /run/secrets/ACCESS_TOKEN)'
```

如果更改 Secret 变量名，记得删掉原来重名的变量（系统变量调用顺序自上而下）。  
![](https://s2.loli.net/2023/07/27/7FtmpO4eVMwqUad.png)
