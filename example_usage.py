#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Scraping Toolkit - 使用示例

这个文件展示了如何使用谷歌搜索爬虫和HTML内容爬虫的基本用法。
"""

import json
import time
from google_search_scraper import GoogleSearchScraper
from html_content_scraper import HTMLContentScraper


def example_google_search():
    """谷歌搜索爬虫使用示例"""
    print("=== 谷歌搜索爬虫示例 ===")
    
    # 创建搜索爬虫实例
    search_scraper = GoogleSearchScraper()
    
    # 搜索示例
    query = "Python web scraping tutorial"
    print(f"搜索关键词: {query}")
    
    try:
        # 执行搜索
        results = search_scraper.search_google(
            query=query,
            num_results=20,  # 获取20个结果
            language='en',   # 英文搜索
            country='us'     # 美国地区
        )
        
        print(f"找到 {len(results)} 个搜索结果")
        
        # 显示前5个结果
        for i, result in enumerate(results[:5], 1):
            print(f"\n{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   描述: {result['snippet'][:100]}...")
        
        # 保存搜索结果
        filename = f"search_results_{int(time.time())}.json"
        search_scraper.save_results(results, filename)
        print(f"\n搜索结果已保存到: {filename}")
        
        return results
        
    except Exception as e:
        print(f"搜索过程中出现错误: {e}")
        return []


def example_html_scraping(urls=None):
    """HTML内容爬虫使用示例"""
    print("\n=== HTML内容爬虫示例 ===")
    
    # 创建HTML爬虫实例
    html_scraper = HTMLContentScraper(output_dir="example_scraped_data")
    
    # 如果没有提供URL，使用默认示例
    if not urls:
        urls = [
            "https://httpbin.org/html",
            "https://example.com",
            "https://httpbin.org/encoding/utf8"
        ]
    
    print(f"准备爬取 {len(urls)} 个URL")
    
    try:
        # 批量爬取
        results = html_scraper.scrape_urls(
            urls=urls,
            delay=2  # 每个请求间隔2秒
        )
        
        # 显示结果统计
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        print(f"\n爬取完成:")
        print(f"  成功: {successful}")
        print(f"  失败: {failed}")
        
        # 显示详细结果
        for result in results:
            status = "✓" if result['success'] else "✗"
            print(f"  {status} {result['url']}")
            if not result['success']:
                print(f"    错误: {result.get('error', 'Unknown error')}")
        
        return results
        
    except Exception as e:
        print(f"爬取过程中出现错误: {e}")
        return []


def example_combined_workflow():
    """组合工作流示例：先搜索，再爬取搜索结果"""
    print("\n=== 组合工作流示例 ===")
    
    # 1. 搜索相关内容
    search_scraper = GoogleSearchScraper()
    
    query = "Python requests library documentation"
    print(f"搜索: {query}")
    
    try:
        search_results = search_scraper.search_google(
            query=query,
            num_results=5,
            language='en'
        )
        
        if not search_results:
            print("没有找到搜索结果")
            return
        
        # 2. 提取URL列表
        urls = [result['url'] for result in search_results]
        print(f"从搜索结果中提取了 {len(urls)} 个URL")
        
        # 3. 爬取这些URL的内容
        html_scraper = HTMLContentScraper(output_dir="combined_workflow_data")
        
        print("开始爬取搜索结果页面...")
        scrape_results = html_scraper.scrape_urls(urls, delay=3)
        
        # 4. 生成报告
        successful_scrapes = [r for r in scrape_results if r['success']]
        
        print(f"\n工作流完成:")
        print(f"  搜索结果: {len(search_results)}")
        print(f"  成功爬取: {len(successful_scrapes)}")
        print(f"  成功率: {len(successful_scrapes)/len(urls)*100:.1f}%")
        
    except Exception as e:
        print(f"组合工作流出现错误: {e}")


def main():
    """主函数 - 运行所有示例"""
    print("Web Scraping Toolkit - 使用示例")
    print("=" * 50)
    
    # 示例1: 谷歌搜索
    search_results = example_google_search()
    
    # 示例2: HTML内容爬取
    example_html_scraping()
    
    # 示例3: 组合工作流
    example_combined_workflow()
    
    print("\n" + "=" * 50)
    print("所有示例运行完成！")
    print("\n提示:")
    print("- 检查生成的文件和目录")
    print("- 根据需要调整参数和配置")
    print("- 遵守网站的robots.txt和使用条款")


if __name__ == "__main__":
    main()