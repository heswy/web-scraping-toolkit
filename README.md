# Web Scraping Toolkit

一个功能强大的Python网页爬虫工具包，包含谷歌搜索结果爬取和HTML内容提取功能。

## 功能特性

### 🔍 谷歌搜索爬虫 (google_search_scraper.py)
- 自动搜索谷歌并获取搜索结果
- 支持多种搜索参数配置（语言、国家、时间范围等）
- 自动处理反爬虫机制
- 支持代理设置
- 结果保存为JSON格式

### 📄 HTML内容爬虫 (html_content_scraper.py)
- 从URL获取完整HTML内容
- 智能编码检测和处理
- 提取纯文本内容
- 处理压缩内容和各种编码格式
- 自动保存HTML和文本文件
- 支持批量处理

## 安装依赖

```bash
pip install -r requirements_opensource.txt
```

## 快速开始

### 1. 谷歌搜索爬虫

```python
from google_search_scraper import GoogleSearchScraper

# 创建爬虫实例
scraper = GoogleSearchScraper()

# 搜索并获取结果
results = scraper.search_google(
    query="Python web scraping",
    num_results=50,
    language='en',
    country='us'
)

# 保存结果
scraper.save_results(results, "search_results.json")
```

### 2. HTML内容爬虫

```python
from html_content_scraper import HTMLContentScraper

# 创建爬虫实例
scraper = HTMLContentScraper(output_dir="scraped_content")

# 爬取单个URL
result = scraper.scrape_url("https://example.com")

# 批量爬取
urls = ["https://example1.com", "https://example2.com"]
results = scraper.scrape_urls(urls, delay=2)
```

## 配置选项

### 代理设置

```python
proxy_config = {
    'http': 'http://proxy-server:port',
    'https': 'https://proxy-server:port'
}

scraper = GoogleSearchScraper(proxy_config=proxy_config)
```

### 搜索参数

- `query`: 搜索关键词
- `num_results`: 结果数量 (默认: 100)
- `language`: 搜索语言 (默认: 'en')
- `country`: 搜索国家 (默认: 'us')
- `time_range`: 时间范围 ('qdr:d', 'qdr:w', 'qdr:m', 'qdr:y')

### HTML爬虫参数

- `output_dir`: 输出目录 (默认: "scraped_content")
- `delay`: 请求延迟秒数 (默认: 1)

## 输出格式

### 搜索结果 (JSON)
```json
[
  {
    "title": "页面标题",
    "url": "https://example.com",
    "snippet": "页面描述",
    "display_url": "example.com",
    "domain": "example.com"
  }
]
```

### HTML爬取结果
- `domain_timestamp.html`: 原始HTML文件
- `domain_timestamp.txt`: 提取的纯文本内容

## 特性说明

### 编码处理
- 使用 `chardet` 库进行智能编码检测
- 多层编码检测策略
- 自动处理UTF-8、GBK、GB2312等常见编码
- 处理压缩内容和损坏的编码

### 反爬虫机制
- 随机请求延迟
- 真实浏览器User-Agent
- 会话保持
- 代理支持

### 错误处理
- 网络超时处理
- 编码错误恢复
- 详细的日志记录
- 优雅的错误降级

## 注意事项

1. **遵守robots.txt**: 请确保遵守目标网站的robots.txt规则
2. **请求频率**: 建议设置适当的延迟，避免对服务器造成压力
3. **法律合规**: 请确保您的爬虫行为符合当地法律法规
4. **代理使用**: 如需要，请配置合适的代理服务器

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 更新日志

### v1.0.0
- 初始版本发布
- 支持谷歌搜索结果爬取
- 支持HTML内容提取
- 智能编码检测
- 代理支持

## 技术支持

如果您在使用过程中遇到问题，请：

1. 查看日志输出获取详细错误信息
2. 检查网络连接和代理设置
3. 确认目标网站是否可访问
4. 提交Issue描述具体问题

---

**免责声明**: 本工具仅供学习和研究使用，请确保您的使用行为符合相关法律法规和网站服务条款。