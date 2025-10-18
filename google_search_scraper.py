#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Search Results Scraper
一个用于爬取谷歌搜索结果的Python工具

功能：
1. 搜索谷歌并获取搜索结果链接
2. 支持多种搜索参数配置
3. 自动处理反爬虫机制
4. 支持代理设置

作者: Open Source Community
许可: MIT License
"""

import requests
import time
import random
import json
from urllib.parse import urlencode, urlparse
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoogleSearchScraper:
    """谷歌搜索结果爬虫"""
    
    def __init__(self, proxy_config: Optional[Dict] = None):
        """
        初始化爬虫
        
        Args:
            proxy_config: 代理配置，格式如 {'http': 'http://proxy:port', 'https': 'https://proxy:port'}
        """
        self.session = requests.Session()
        self.proxy_config = proxy_config
        
        # 设置请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(self.headers)
        
        if self.proxy_config:
            self.session.proxies.update(self.proxy_config)
            logger.info("已配置代理设置")
    
    def search_google(self, query: str, num_results: int = 100, language: str = 'en', 
                     country: str = 'us', time_range: str = None) -> List[Dict]:
        """
        搜索谷歌并获取结果
        
        Args:
            query: 搜索关键词
            num_results: 需要的结果数量
            language: 搜索语言 (en, zh-cn, etc.)
            country: 搜索国家 (us, cn, etc.)
            time_range: 时间范围 (qdr:d, qdr:w, qdr:m, qdr:y)
        
        Returns:
            包含搜索结果的列表，每个结果包含title, url, snippet等信息
        """
        results = []
        start = 0
        
        while len(results) < num_results:
            # 构建搜索URL
            params = {
                'q': query,
                'start': start,
                'num': min(10, num_results - len(results)),
                'hl': language,
                'gl': country,
            }
            
            if time_range:
                params['tbs'] = time_range
            
            search_url = f"https://www.google.com/search?{urlencode(params)}"
            
            try:
                logger.info(f"正在搜索: {query} (第 {start//10 + 1} 页)")
                
                # 发送请求
                response = self.session.get(search_url, timeout=30)
                response.raise_for_status()
                
                # 解析结果
                page_results = self._parse_search_results(response.text)
                
                if not page_results:
                    logger.warning("未找到更多搜索结果，停止搜索")
                    break
                
                results.extend(page_results)
                start += 10
                
                # 随机延迟，避免被封
                time.sleep(random.uniform(2, 5))
                
            except requests.RequestException as e:
                logger.error(f"搜索请求失败: {e}")
                break
            except Exception as e:
                logger.error(f"解析搜索结果时出错: {e}")
                break
        
        logger.info(f"搜索完成，共获取 {len(results)} 个结果")
        return results[:num_results]
    
    def _parse_search_results(self, html: str) -> List[Dict]:
        """
        解析谷歌搜索结果页面
        
        Args:
            html: 搜索结果页面的HTML
        
        Returns:
            解析后的搜索结果列表
        """
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # 查找搜索结果容器
        search_results = soup.find_all('div', class_='g')
        
        for result in search_results:
            try:
                # 提取标题和链接
                title_element = result.find('h3')
                if not title_element:
                    continue
                
                link_element = result.find('a')
                if not link_element or not link_element.get('href'):
                    continue
                
                title = title_element.get_text(strip=True)
                url = link_element['href']
                
                # 过滤无效链接
                if not url.startswith('http'):
                    continue
                
                # 提取描述
                snippet_element = result.find('span', class_=['aCOpRe', 'st'])
                snippet = snippet_element.get_text(strip=True) if snippet_element else ""
                
                # 提取显示URL
                cite_element = result.find('cite')
                display_url = cite_element.get_text(strip=True) if cite_element else url
                
                result_data = {
                    'title': title,
                    'url': url,
                    'snippet': snippet,
                    'display_url': display_url,
                    'domain': urlparse(url).netloc
                }
                
                results.append(result_data)
                
            except Exception as e:
                logger.warning(f"解析单个搜索结果时出错: {e}")
                continue
        
        return results
    
    def save_results(self, results: List[Dict], filename: str):
        """
        保存搜索结果到JSON文件
        
        Args:
            results: 搜索结果列表
            filename: 保存的文件名
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"搜索结果已保存到: {filename}")
        except Exception as e:
            logger.error(f"保存文件时出错: {e}")

def main():
    """主函数示例"""
    # 创建爬虫实例
    scraper = GoogleSearchScraper()
    
    # 示例搜索
    query = "Python web scraping tutorial"
    results = scraper.search_google(
        query=query,
        num_results=50,
        language='en',
        country='us'
    )
    
    # 保存结果
    if results:
        scraper.save_results(results, f"google_search_results_{int(time.time())}.json")
        
        # 打印前几个结果
        print(f"\n搜索关键词: {query}")
        print(f"共找到 {len(results)} 个结果\n")
        
        for i, result in enumerate(results[:5], 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   描述: {result['snippet'][:100]}...")
            print()

if __name__ == "__main__":
    main()