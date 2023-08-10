---
title: Playwright 编写签到脚本遇到的问题
date: 2023-07-23T16:28:15+08:00
draft: false
tags: ["playwright"]
categories: ["playwright"]
---

## browser
一行命令完成安装依赖和浏览器。

    playwright install --with-deps chromium firefox

## 万能的 record 模式
参考 [[playwright 五分钟上手指南]]，遇到任何定位问题直接哪里不会点哪里。
```python
await page.pause()
```

## 官方文档不推荐的写法
参考 [Auto-waiting](https://playwright.dev/python/docs/actionability)，绝大部分方法都会自动等待页面加载完成才执行相应操作，超过系统默认超时时间（30s）才会报错。
```python
# https://playwright.dev/python/docs/api/class-page#page-wait-for-timeout
await page.wait_for_timeout(1000)   # DISCOURAGED
await page.wait_for_load_state("networkidle")   # 等待网络加载完成
```

[XPath locator](https://playwright.dev/python/docs/other-locators#xpath-locator)和 [CSS locator](https://playwright.dev/python/docs/other-locators#css-locator) 也是不推荐的，更直观的写法是使用 Locator 的各种定位 API。  
![](https://s2.loli.net/2023/07/26/2PEJN9hAwk3eOXc.png)

要等待某个元素出现选 is_enabled() | focus() 优于 is_visible()。  
is_visible() 在 headless = False 下没有问题，但调试的下切换到其他窗口，is_visible() 就会失去聚焦对象。

## playwright.\_impl.\_api_types.Error: Playwright connection closed
多半是过度封装创建函数导致的。page 对象一旦跳出 `async with async_playwright() as playwright:` 上下文就无法获取 `browser | context` 原来的属性。

## 代理
```python
async with async_playwright() as playwright:
    # 对整个 browser 设置代理
    browser = await playwright.firefox.launch(headless=browser_headless, proxy=browser_proxy)
    context = await browser.new_context()
    
    # 对不同 context 设置代理
    browser = await playwright.firefox.launch(headless=False)
    context = await browser.new_context(proxy=browser_proxy)
```

## v2ex
点击签到按钮提示：“你的浏览器有一些奇奇怪怪的设置，请用一个干净安装的浏览器重试一下吧”。  
原因：[首页 referer 与其他页不匹配](https://www.v2ex.com/t/846469)。  
解决办法：得先回首页再跳转到签到页面。  
```python
await goto(home_url)
await goto(sign_url)
```

## b站直播间
使用 chromium 提示浏览器版本过低，firefox 则没问题。  
![](https://s2.loli.net/2023/07/26/BSTfLRrAn6FUuPY.png)

同时提示：Cannot read properites of null (reading 'sendDanmaku')  
![](https://s2.loli.net/2023/07/26/hv59PLiaOYNgmWF.png)

## 鼠标悬停
[hover](https://playwright.dev/python/docs/api/class-locator#locator-hover) 或 [focus](https://playwright.dev/python/docs/api/class-locator#locator-focus)。

## 模拟正常输入
```python
type('123', delay=1000)  # 每个字的输入间隔为一秒
```

## 多个匹配元素报错

    strict mode violation: get_by_placeholder("发个弹幕呗~") resolved to 2 elements

直接 `await page.pause()` 开启调试模式找出是第几顺位的元素，根据情况使用：`first、last、nth()`。
```python
# exact=True 精准匹配
print(await page.get_by_text("发个弹幕呗").count())
await page.get_by_placeholder("发个弹幕呗~").nth(1).fill("2")
await page.get_by_text("发送", exact=True).nth(1).click():
```

## docker 容器的定位超时问题
原理不明，本地测试通过而 huggingface 运行第一种写法的代码会超时。
```python
# ×
if await page.get_by_text("你无任何进行任务", exact=True).is_enabled()
#√
if page.get_by_text("你无任何进行任务", exact=True) 
```

## 多线程
文档确说明 [**Playwright's API is not thread-safe**](https://playwright.dev/python/docs/library#threading)，[issue/623](https://github.com/microsoft/playwright-python/issues/623) 也有人给出多线程的实现，但还是推荐使用 async 完成。

## 多进程 
同上，与其手动处理进程资源（开销），不如直接 async。

## 多 context & 多 page
文档推荐的写法：[Multiple Contexts in a Single Test](https://playwright.dev/python/docs/browser-contexts#multiple-contexts-in-a-single-test)，通过示例可以看出 playwright 自上而下的资源创建过程：

1. 创建全局 browser 浏览器对象，
2. 创建一个或多个 context 对象；
3. 每个 context 又可以创建一个或多个 page对象。

可以理解为在一个任务里面只有一个谷歌浏览器（browser），可以拥有多个谷歌账号（context）， 每个账号（local storage）可以存储所有标签页（page） 的 cookie 信息。  

也就是说：

> 只有一个 page 对象在遇到耗时任务时一定会持续等待当前任务完成，async/await 无法发挥作用，完成时间和串行完成任务没区别。
> 
> 一个 context 下启动多个 page 也是近乎串行完成任务。而且启动多个 page 会占用资源，其他 page 一直在等上一个 page 完成任务才能开始工作。
> 
> 真正意义上的异步同时完成任务就得分别创建多个 browser 对象。 

可以简单测试单个 page 和 多个 page 的区别。先启动一个 fastapi 服务器，设置两个耗时任务。  
```python
import time

from fastapi import FastAPI
from uvicorn import run

app = FastAPI()

# 一！
@app.get("/sleep_one_second")
async def sleep_one_second():
    time.sleep(1)
    return {"res": 1}
    
# 五！
@app.get("/sleep_five_second")
async def sleep_five_second():
    time.sleep(5)
    return {"res": 5}


if __name__ == "__main__":
    run("server:app", host="0.0.0.0", port=8000, reload=True
       
```

测试 single/multi page 的执行时间。  
```python
import asyncio
import time

from functools import wraps
from playwright.async_api import async_playwright


def timeit(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        s_time = time.perf_counter()
        await func(*args, **kwargs)
        print(f"{func.__name__} cost {time.perf_counter() - s_time}s")
    return loop.create_task(wrapper())
  
async def single_page(playwright):
    chromium = playwright.chromium
    browser = await chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("http://localhost:8000/sleep_one_second")
    await page.goto("http://localhost:8000/sleep_five_second")
    await browser.close()

async def multi_page(playwright):
    chromium = playwright.chromium
    browser = await chromium.launch(headless=False)
    context = await browser.new_context()
    page1 = await context.new_page()
    page5 = await context.new_page()
    await page1.goto("http://localhost:8000/sleep_one_second")
    await page5.goto("http://localhost:8000/sleep_five_second")
    await browser.close()

@timeit
async def main():
    async with async_playwright() as playwright:
        await single_page(playwright)
        # await multi_page(playwright)
  

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        exit()
```

分别注释执行你会发现两个任务都是 8秒4（创建浏览器+执行任务+关闭浏览器） 左右完成，和上面分析一样。

**一个浏览器环境下并不会影响执行时间，创建多个 page 只是便于区分任务。**

## 多开
如果还是不死心，一定要双开多开，以下写法也是可行的。  
```python
import asyncio
import time
from playwright.async_api import async_playwright


async def init_page(playwright):
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    return page
    
async def sleep_one_second(playwright):
    page = await init_page(playwright)
    await page.goto("http://localhost:8000/sleep_one_second")
    await page.close()

async def sleep_five_second(playwright):
    page = await init_page(playwright)
    await page.goto("http://localhost:8000/sleep_five_second")
    await page.close()


async def main():
    async with async_playwright() as playwright:
        task1 = asyncio.create_task(sleep_one_second(playwright))
        task2 = asyncio.create_task(sleep_five_second(playwright))
        tasks = [task1, task2]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    s_time = time.perf_counter()
    asyncio.run(main())
    print(f"cost {time.perf_counter() - s_time}s")
```

因为创建了两个浏览器对象，耗时多了一秒。  
![](https://s2.loli.net/2023/07/26/hocCpS8ZYHfQaBy.png)

