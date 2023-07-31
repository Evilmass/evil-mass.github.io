---
title: playwright 快速上手指南
date: 2023-07-23T01:15:31+08:00
draft: false
tags: ["playwright"]
categories: ["playwright"]
---

本文旨在“快速上手”，所以不会像其他文章一样详细介绍每一个模块，具体用法请根据实际需求翻阅[官方文档](https://playwright.dev/python/docs/api/class-page)。

## 安装
```pip
pip3 install playwright
playwright install chromium firefox
```

## 调试模式 & 生成代码
自动生成代码：

    playwright codegen -o test.py -b chromium

1. 调试模式会自动记录并生成代码。
![](https://s2.loli.net/2023/07/23/no5YHAKX16PhWLv.png)

2. 移动到相应位置显示元素定位代码，填入相关验证信息，点击登录。
![](https://s2.loli.net/2023/07/23/S5vxr72gXHe4Fn1.png)

右边的调试窗口已经自动生成刚才的登录流程代码（同步）了，将操作部分的代码加 `await` 改成异步即可。
```python
import asyncio
from playwright.async_api import async_playwright


async def main():
    """  
    headless = False，显示界面
    slow_mo，模仿用户在一秒内完成每一步操作
    """
    async with async_playwright() as p:
        # 初始化浏览器
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context()
        page = await context.new_page()
        # 跳转到 Gihub 登录页面
        await page.goto("https://github.com/login")
        # 填入验证信息，type 是打字，fill 是复制粘贴
        await page.get_by_label("Username or email address").type("username", delay=2000)
        await page.get_by_label("Password").fill("password")
        # 点击登录按钮
        await page.get_by_role("button", name="Sign in").click()


if __name__ == "__main__":
    asyncio.run(main())

```

平时只需要 `await page.pause()` 然后在 record 模式下定位元素，开发效率极高。

动画使用 [Screen To Gif](https://www.screentogif.com/) 录制。
![login.gif](https://s2.loli.net/2023/07/23/jMiRLtrVAqW4SDY.gif)

## 练习站点
https://sahitest.com/demo

想掌握 playwright 各种用法，建议用心过一遍。  
![](https://s2.loli.net/2023/07/26/ZcpbDdRMNjGCf37.png)

![](https://s2.loli.net/2023/07/26/8qJfGvKcETX4khg.png)