#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML Content Scraper
一个用于从网页URL获取和解析HTML内容的Python工具

功能：
1. 从URL获取HTML内容
2. 自动检测和处理编码问题
3. 提取纯文本内容
4. 支持代理和自定义请求头
5. 处理压缩内容和各种编码格式

作者: Open Source Community
许可: MIT License
"""

import requests
import time
import chardet
from bs4 import BeautifulSoup
import logging
from typing import Dict, Optional, List
from urllib.parse import urlparse
import re
from datetime import datetime
import os

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HTMLContentScraper:
    """HTML内容爬虫"""
    
    def __init__(self, proxy_config: Optional[Dict] = None, output_dir: str = "scraped_content"):
        """
        初始化爬虫
        
        Args:
            proxy_config: 代理配置
            output_dir: 输出目录
        """
        self.session = requests.Session()
        self.proxy_config = proxy_config
        self.output_dir = output_dir
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 设置请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN,zh;q=0.8',
            'Accept-Encoding': 'identity',  # 禁用压缩以避免编码问题
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
        }
        self.session.headers.update(self.headers)
        
        if self.proxy_config:
            self.session.proxies.update(self.proxy_config)
            logger.info("已配置代理设置")
    
    def scrape_url(self, url: str, delay: int = 1) -> Dict:
        """
        爬取单个URL的内容
        
        Args:
            url: 要爬取的URL
            delay: 请求延迟（秒）
        
        Returns:
            包含爬取结果的字典
        """
        result = {
            'url': url,
            'success': False,
            'html_content': '',
            'text_content': '',
            'text_length': 0,
            'encoding': '',
            'error': '',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            logger.info(f"正在爬取: {url}")
            
            # 添加延迟
            if delay > 0:
                time.sleep(delay)
            
            # 获取HTML内容
            html_result = self._get_html(url)
            
            if not html_result['success']:
                result['error'] = html_result['error']
                return result
            
            result['html_content'] = html_result['content']
            result['encoding'] = html_result['encoding']
            
            # 提取文本内容
            text_content = self._extract_text(html_result['content'])
            
            # 检查内容是否损坏
            if self._is_text_corrupted(text_content):
                logger.warning(f"检测到损坏的文本内容，尝试修复: {url}")
                # 这里可以添加更多修复逻辑
            
            result['text_content'] = text_content
            result['text_length'] = len(text_content)
            result['success'] = True
            
            # 保存内容到文件
            self._save_content(url, html_result['content'], text_content)
            
            logger.info(f"✅ 成功爬取: {url} (文本长度: {len(text_content)})")
            
        except Exception as e:
            error_msg = f"爬取失败: {str(e)}"
            result['error'] = error_msg
            logger.error(f"❌ {url} - {error_msg}")
        
        return result
    
    def _get_html(self, url: str) -> Dict:
        """
        获取网页HTML内容并处理编码
        
        Args:
            url: 网页URL
        
        Returns:
            包含HTML内容和编码信息的字典
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # 检查是否为压缩内容
            content_encoding = response.headers.get('content-encoding', '').lower()
            if content_encoding in ['gzip', 'deflate', 'br']:
                logger.warning(f"检测到压缩内容: {content_encoding}")
            
            # 多层编码检测策略
            encoding = self._detect_encoding(response)
            
            # 使用检测到的编码解码内容
            try:
                content = response.content.decode(encoding, errors='replace')
            except (UnicodeDecodeError, LookupError):
                # 如果解码失败，使用UTF-8并替换错误字符
                content = response.content.decode('utf-8', errors='replace')
                encoding = 'utf-8 (fallback)'
            
            logger.info(f"编码检测结果: {encoding}")
            
            return {
                'success': True,
                'content': content,
                'encoding': encoding,
                'error': ''
            }
            
        except requests.RequestException as e:
            return {
                'success': False,
                'content': '',
                'encoding': '',
                'error': f"网络请求错误: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'content': '',
                'encoding': '',
                'error': f"获取HTML时出错: {str(e)}"
            }
    
    def _detect_encoding(self, response) -> str:
        """
        多层编码检测策略
        
        Args:
            response: requests响应对象
        
        Returns:
            检测到的编码
        """
        # 1. 使用chardet检测
        try:
            detected = chardet.detect(response.content)
            if detected and detected['confidence'] > 0.7:
                logger.info(f"chardet检测: {detected['encoding']} (置信度: {detected['confidence']:.2f})")
                return detected['encoding']
        except Exception as e:
            logger.warning(f"chardet检测失败: {e}")
        
        # 2. 从HTTP头获取编码
        content_type = response.headers.get('content-type', '')
        if 'charset=' in content_type:
            try:
                charset = content_type.split('charset=')[1].split(';')[0].strip()
                logger.info(f"HTTP头编码: {charset}")
                return charset
            except Exception:
                pass
        
        # 3. 尝试常见编码
        common_encodings = ['utf-8', 'gbk', 'gb2312', 'big5', 'iso-8859-1', 'windows-1252']
        
        for encoding in common_encodings:
            try:
                response.content.decode(encoding)
                logger.info(f"成功使用编码: {encoding}")
                return encoding
            except (UnicodeDecodeError, LookupError):
                continue
        
        # 4. 最后回退到UTF-8
        logger.warning("所有编码检测都失败，使用UTF-8作为回退")
        return 'utf-8'
    
    def _extract_text(self, html_content: str) -> str:
        """
        从HTML中提取纯文本内容
        
        Args:
            html_content: HTML内容
        
        Returns:
            提取的纯文本
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 移除脚本和样式标签
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            # 获取文本内容
            text = soup.get_text()
            
            # 清理文本
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            logger.error(f"提取文本时出错: {e}")
            return ""
    
    def _is_text_corrupted(self, text: str) -> bool:
        """
        检查文本是否损坏（包含大量乱码）
        
        Args:
            text: 要检查的文本
        
        Returns:
            如果文本损坏返回True
        """
        if not text or len(text) < 100:
            return True
        
        # 检查替换字符的比例
        replacement_chars = text.count('�')
        if replacement_chars > len(text) * 0.05:  # 超过5%的替换字符
            return True
        
        # 检查控制字符
        control_chars = sum(1 for c in text if ord(c) < 32 and c not in '\n\r\t')
        if control_chars > len(text) * 0.02:  # 超过2%的控制字符
            return True
        
        # 检查非打印字符
        non_printable = sum(1 for c in text if not c.isprintable() and c not in '\n\r\t')
        if non_printable > len(text) * 0.03:  # 超过3%的非打印字符
            return True
        
        # 检查连续特殊字符模式
        special_pattern = re.compile(r'[^\w\s]{10,}')
        if special_pattern.search(text):
            return True
        
        return False
    
    def _save_content(self, url: str, html_content: str, text_content: str):
        """
        保存内容到文件
        
        Args:
            url: 原始URL
            html_content: HTML内容
            text_content: 文本内容
        """
        try:
            # 生成文件名
            domain = urlparse(url).netloc.replace('www.', '')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"{domain}_{timestamp}"
            
            # 保存HTML文件
            html_filename = os.path.join(self.output_dir, f"{base_filename}.html")
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # 保存文本文件
            txt_filename = os.path.join(self.output_dir, f"{base_filename}.txt")
            with open(txt_filename, 'w', encoding='utf-8') as f:
                f.write(f"URL: {url}\n")
                f.write(f"爬取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                f.write(text_content)
            
            logger.info(f"内容已保存: {base_filename}")
            
        except Exception as e:
            logger.error(f"保存文件时出错: {e}")
    
    def scrape_urls(self, urls: List[str], delay: int = 2) -> List[Dict]:
        """
        批量爬取多个URL
        
        Args:
            urls: URL列表
            delay: 每次请求间的延迟
        
        Returns:
            爬取结果列表
        """
        results = []
        
        for i, url in enumerate(urls, 1):
            logger.info(f"[{i}/{len(urls)}] 处理: {url}")
            
            result = self.scrape_url(url, delay)
            results.append(result)
            
            # 显示进度
            success_count = sum(1 for r in results if r['success'])
            success_rate = (success_count / i) * 100
            logger.info(f"进度: {i}/{len(urls)} ({i/len(urls)*100:.1f}%) | 成功率: {success_rate:.1f}%")
        
        return results

def main():
    """主函数示例"""
    # 创建爬虫实例
    scraper = HTMLContentScraper(output_dir="scraped_content")
    
    # 示例URL列表
    test_urls = [
        "https://www.example.com",
        "https://httpbin.org/html",
        "https://www.python.org"
    ]
    
    # 批量爬取
    results = scraper.scrape_urls(test_urls, delay=2)
    
    # 统计结果
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    print(f"\n爬取完成!")
    print(f"总数: {len(results)}")
    print(f"成功: {successful}")
    print(f"失败: {failed}")
    print(f"成功率: {successful/len(results)*100:.2f}%")

if __name__ == "__main__":
    main()