# 为弹幕姬 ReTTS-Cat 插件搭建自定义 tts 引擎


上回说到，在 huggingface 搭建好 vits server 后，平时直播的弹幕语音靠 bilive_dm 播报，有时候口糊听不清还要切窗口看一眼。然后看到弹幕姬有个自定义 tts 引擎，故考虑接入试试。

## Re: TTSCat
[Re: TTSCat 插件](https://www.danmuji.org/plugins/Re-TTSCat) 以及 [仓库地址](https://github.com/Elepover/RE-TTSCat)

开幕 archived 问题不大。
![](https://s2.loli.net/2023/05/23/lUJhum3QTcxenri.png)

插件页面有自定义 tts 引擎 url 的参考格式，怎么简单怎么来（GET）。
![](https://s2.loli.net/2023/05/23/lTxAW7ejmJ21Bsb.png)

在临时目录添加一个 mp3 文件并启动 http 服务器
```python
    python3 -m http.server
    # 自定义引擎地址填入如下 url
    https://127.0.0.1:8000?text=$TTSTEXT
```

语音成功播放后感觉 `so easy`，然后如无意外的出现意外了。

## 踩坑
fastapi 写个简单 get 接口。
```python
@app.get("/voice")
async def get_audio(token: str, text: str):
    if token != os.environ.get("token"):
        return {"code": 401}
    # vits 合成语音，返回二进制文件
    audio = load_fast_vits(text)
    if audio is None:
        return {"code": 500}
    else:
        return FileResponse(audio)
```

发送弹幕后什么都没有发生，打开调试模式看看怎么回事。
![](https://s2.loli.net/2023/05/23/n4eYkaQROAhBG51.png)

一切正常，还是什么都没有发生。
![](https://s2.loli.net/2023/05/23/hJzGt91fqwTSBZR.png)

在缓存目录下找到 get 获取到的音频文件，直接播放没有问题。

### 坑1
切换到 `dotNet` 引擎，找到缓存下的文件，然后用回 python http 服务器测试，无声音。

切换到 `百度` 引擎得到音频文件后测试正常播放，迷惑。

### 坑2
已知 vits 语音合成使用了 scipy 库，默认生成的是 wav 格式的音频。感觉是格式问题，然后就犯了个错误：图省事直接用 `scipy.io.write` 方法生成 mp3 文件。

结果无法播放，调试选项依旧不报错。

## Google Search
即便是谷歌搜索，在遇到冷门问题时也不一定有替代方案，不过万幸还是找到一个：[MsTtsForBiliLiveDm](https://github.com/Youmiel/MsTtsForBiliLiveDm.git)。
![](https://s2.loli.net/2023/05/23/KLeUrgFGBPfIjxh.png)

仓库 archived 是因为微软关停了免费的网页 tts 服务（被短视频合成语音薅怕了估计）。
![](https://s2.loli.net/2023/05/23/x3k2NqPmWTszr1Q.png)

项目原理是通过微软免费的网页 tts 下载对应音频后接入弹幕姬。但是这更疑惑了，都是生成的 mp3 格式，为什么 vits 后端生成的音频就播放不了呢？

还是直接联系一下作者吧，熟练的 `git clone`、`git log`，然后：

```python
    commit 01cd771f3a7187746849f81632a74b56c5470ed6 (HEAD -> master, origin/master, origin/HEAD)
    Author: Youmiel <70473080+Youmiel@users.noreply.github.com>
    Date:   Thu May 11 14:57:29 2023 +0800

        Archive repository.
```

这倒是提醒我也该设置[邮箱隐私保护](https://docs.github.com/zh/enterprise-cloud@latest/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-email-preferences/setting-your-commit-email-address)了，继续谷歌。

![](https://s2.loli.net/2023/05/23/B9PfxjRVsGvYhpi.png)

![](https://s2.loli.net/2023/05/23/VXRUrbxTpYm2Zj7.png)

要是作者不用相同 ID，这篇文章就出不来了（

私信后问题解决了，得用原生 mp3 格式。所以坑2偷懒直接生成 mp3 是不行的，得 `wav 转 mp3`。
![](https://s2.loli.net/2023/05/23/fSKUhQzT7dBcL3W.png)

后面又翻了下 [NAudio Wiki](https://github.com/naudio/NAudio/wiki/Playing-an-Audio-File#loading-the-file)，是支持 wav 和 mp3 的。
![](https://s2.loli.net/2023/05/23/9WCrXQPwvOAUY5D.png)

Re-TTS CAT 的[实现](https://github.com/Elepover/RE-TTSCat/blob/81f2bdcc678af3f71f47351317ed522f7dfe0f17/Re_TTSCat/TTSHelper/TTSPlayer.Play.cs)看上去也没问题，大概是 bug 吧。
![](https://s2.loli.net/2023/05/23/sWVUgHxAqz5BoOu.png)

## wav to mp3
ffmpeg yes！
```python
import subprocess

subprocess.run(
    cmd="ffmpeg.exe -i test.wav test.mp3",
    shell=True
)
```

## 坑3
本地测试正常了，DockerFile 加个 ffmpeg 的依赖，代码一加直接往 huggingface 推送，然后报了 `Permission Denied` 错误。

```python
  File "/usr/local/lib/python3.9/os.py", line 225, in makedirs
    mkdir(name, mode)
    PermissionError: [Errno 13] Permission denied: 'flagged'
```

一开始直接 `chmod 777 /ttscache` 还是会报错，然后[官方文档](https://huggingface.co/docs/hub/spaces-sdks-docker)建议新增一个用户并挂载目录，这样就没有读写权限问题了。

![](https://s2.loli.net/2023/05/23/UDnHWqtBa98IoSN.png)

ffmpeg 正常转码输出 mp3 文件
![](https://s2.loli.net/2023/05/23/zRxQohDJHSWmUjC.png)
