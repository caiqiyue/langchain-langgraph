# -*- coding: utf-8 -*-
"""
【案例 2】Python 爬虫工具箱
=============================

本案例展示 Python 爬虫的常用工具库。

请求库：
- requests：同步库，"HTTP for Humans"
- aiohttp：异步库，高并发抓取
- httpx：同时支持同步和异步

解析库：
- BeautifulSoup (bs4)：解析 HTML，人性化 API
- lxml：高速解析，支持 XPath
- regex：正则表达式，强大文本匹配

浏览器自动化：
- Selenium / Playwright：控制真实浏览器

框架：
- Scrapy：功能强大的异步爬虫框架

要点：
1. 掌握请求库的用法
2. 理解解析库的特点
3. 了解浏览器自动化工
"""

# ============================================================
# 1. 环境配置
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("=" * 60)
print("案例 2: Python 爬虫工具箱")
print("=" * 60)

# ============================================================
# 2. 请求库
# ============================================================
print("\n【请求库】")
print("-" * 50)

请求库表 = """
| 库        | 特点              | 适用场景                |
|-----------|------------------|------------------------|
| requests  | 同步，语法极简     | 中小规模爬虫            |
| aiohttp   | 异步，高并发        | 海量页面抓取            |
| httpx     | 同步+异步，支持 HTTP/2 | 现代应用            |
"""
print(请求库表)

print("""
requests 示例：
  import requests
  response = requests.get('https://www.python.org')
  print(response.status_code)
  print(response.text[:50])

aiohttp 示例：
  import aiohttp
  async with aiohttp.ClientSession() as session:
      async with session.get(url) as response:
          return await response.text()
""")

# ============================================================
# 3. 解析库
# ============================================================
print("\n【解析库】")
print("-" * 50)

解析库表 = """
| 库           | 特点                  | 适用场景            |
|--------------|----------------------|---------------------|
| BeautifulSoup| API 人性化            | 格式混乱的 HTML     |
| lxml         | 高速，C 语言实现       | 大规模数据提取      |
| regex        | 强大文本匹配          | 非结构化数据         |
"""
print(解析库表)

print("""
BeautifulSoup 示例：
  from bs4 import BeautifulSoup
  soup = BeautifulSoup(html, 'html.parser')
  soup.find('h1').text

lxml XPath 示例：
  from lxml import etree
  html = etree.HTML(html_string)
  html.xpath('//h1/text()')

regex 示例：
  import re
  re.search(r'[\w.-]+@[\w.-]+', text).group()
""")

# ============================================================
# 4. 浏览器自动化
# ============================================================
print("\n【浏览器自动化】")
print("-" * 50)

print("""
Selenium / Playwright：
  - 控制真实浏览器（Chrome, Firefox）
  - 处理 JavaScript 动态渲染内容
  - 支持点击、滚动、输入等用户操作

Playwright 示例：
  from playwright.async_api import async_playwright
  async with async_playwright() as p:
      browser = await p.chromium.launch()
      page = await browser.new_page()
      await page.goto('https://example.com')
""")

# ============================================================
# 5. 爬虫框架
# ============================================================
print("\n【爬虫框架】")
print("-" * 50)

print("""
Scrapy：
  - 功能强大的异步爬虫框架
  - 内置去重、管道存储、中间件
  - 适合大规模、高性能工程化爬虫

Scrapy 示例：
  import scrapy
  class MySpider(scrapy.Spider):
      name = "my_spider"
      start_urls = ['http://example.com']

      def parse(self, response):
          for item in response.css('div.item'):
              yield {'title': item.css('h2::text').get()}
""")

print("\n" + "=" * 60)
print("案例结束")
print("=" * 60)