import logging
from playwright.async_api import async_playwright, Browser, BrowserContext
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class BrowserPool:
    """
    Playwright 浏览器池与反爬封装。
    提供安全的 Browser Context，注入随机 UA，并可配合 stealth 脚本抹除自动化指纹。
    """
    def __init__(self):
        self._playwright = None
        self._browser: Browser = None
        self.ua = UserAgent(platforms='pc')

    async def start(self):
        """初始化 Playwright 和无头浏览器"""
        if not self._playwright:
            self._playwright = await async_playwright().start()
            # 默认使用 chromium，真实场景下可以随机切换
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-infobars',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            )
            logger.info("Playwright browser started.")

    async def get_context(self) -> BrowserContext:
        """获取一个隔离的浏览器上下文，注入随机 UA"""
        if not self._browser:
            await self.start()
            
        random_ua = self.ua.random
        context = await self._browser.new_context(
            user_agent=random_ua,
            viewport={'width': 1920, 'height': 1080}
        )
        
        # 注入 stealth 脚本，抹除 navigator.webdriver
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        return context

    async def close(self):
        """清理资源"""
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        logger.info("Playwright browser closed.")

browser_pool = BrowserPool()
