import asyncio
from playwright.async_api import async_playwright


async def main():
    """
    headless = False，显示界面
    slow_mo = 1500，模仿用户在 1.5 秒内完成每一步操作
    type 和 fill 都是输入参数，type 加上 delay = 100 代表每 0.1 秒输入一个字符
    """
    async with async_playwright() as p:
        # 初始化浏览器
        browser = await p.chromium.launch(headless=False, slow_mo=1500)
        context = await browser.new_context()
        page = await context.new_page()
        # 跳转到 Gihub 登录页面
        await page.goto("https://github.com/login")
        # 填入验证信息
        await page.get_by_label("Username or email address").type("username", delay=100)
        await page.get_by_label("Password").fill("password")
        # 点击登录按钮
        await page.get_by_role("button", name="Sign in").click()


if __name__ == "__main__":
    asyncio.run(main())
