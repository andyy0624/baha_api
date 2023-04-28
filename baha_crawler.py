# 重構crawler
import requests
from url_utils import UrlBuilder
from bs4 import BeautifulSoup
from typing import Union, Optional
import time
import random as rd
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
}

BAHA_URL = "https://forum.gamer.com.tw"
B_PAGE = "B.php"
C_PAGE = "C.php"


class BahaCrawler():
    def __init__(self) -> None:
        pass
    
    def _get_article_urls_page(self, bsn: Union[int,str], page: Union[int,str]) -> list:
        url_builder = UrlBuilder(f"{BAHA_URL}/{B_PAGE}")
        url = url_builder(bsn=bsn, page=page)
        r = requests.get(url, headers=HEADERS)
        if r.status_code != requests.codes.ok:
            return [{"Error": "網頁載入失敗",
                     "URL": url}]

        article_url_list = []
        soup = BeautifulSoup(r.text, features='lxml')
        item_blocks = soup.select('table.b-list tr.b-list-item')
        if len(item_blocks)==0:
            return [{"Error": "網頁沒有任何文章列表，你可能指向了錯誤的頁面",
                     "URL": url}]
        
        for item_block in item_blocks:
            title_block = item_block.select_one('.b-list__main__title')
            article_url = f"{BAHA_URL}/{title_block.get('href')}"
            article_url_list += [article_url]
        return article_url_list
    
    def get_article_urls_pages(self, bsn: Union[int,str], page_start: Union[int,str], page_end: Optional[Union[int,str]]=None) -> list:
        if page_end is None:
            page_end = page_start
        article_urls = []
        for i in range(page_start, page_end+1):
            article_urls += self._get_article_urls_page(bsn, i)
        return article_urls
    
    def get_article_contents(self, bsn: Union[int,str], snA: Union[int,str]) -> dict:
        url_builder = UrlBuilder(f"{BAHA_URL}/{C_PAGE}")
        url = url_builder(bsn=bsn, snA=snA)
        
        r = requests.get(url, headers=HEADERS)
        if r.status_code != requests.codes.ok:
            return [{"Error": "網頁載入失敗",
                     "URL": url}]
            
        soup = BeautifulSoup(r.text, features='lxml')
        a = soup.select_one('h1.c-post__header__title')
        if a is None:
            article_title = "Error, 抓不到該文章標題"
        else:
            article_title = a.text
        # 抓取回覆總頁數
        article_total_page = self._get_article_total_pageNum(soup)
        # 爬取每一頁回覆
        reply_info_list = []
        url_builder_forPage = UrlBuilder(url)
        for page in range(article_total_page):
            crawler_url = url_builder_forPage(page=page+1)
            reply_list = self._get_reply_info_list(crawler_url)
            reply_info_list.extend(reply_list)
            time.sleep(rd.random()*10)

        article_info = {
            'title': article_title,
            'url': url,
            'reply': reply_info_list
        }
        return article_info
    
    def _get_article_total_pageNum(self, soup: BeautifulSoup) -> int:
        """取得文章總頁數"""
        article_total_page = soup.select_one('.BH-pagebtnA > a:last-of-type').text
        return int(article_total_page)
    
    def _get_reply_info_list(self, url: str) -> list:
        """爬取回覆列表"""
        r = requests.get(url, headers=HEADERS)
        if r.status_code != requests.codes.ok:
            return [{"Error": "網頁載入失敗",
                     "URL": url}]

        reply_info_list = []
        soup = BeautifulSoup(r.text, features='lxml')
        reply_blocks = soup.select('section[id^="post_"]')

        # 對每一則回覆解析資料
        for reply_block in reply_blocks:
            reply_info = {}

            reply_info['floor'] = int(reply_block.select_one('.floor').get('data-floor'))
            reply_info['user_name'] = reply_block.select_one('.username').text
            reply_info['user_id'] = reply_block.select_one('.userid').text

            publish_time = reply_block.select_one('.edittime').get('data-mtime')
            reply_info['publish_time'] = datetime.strptime(publish_time, '%Y-%m-%d %H:%M:%S')

            reply_info['content'] = reply_block.select_one('.c-article__content').text

            gp_count = reply_block.select_one('.postgp span').text
            if gp_count == '-':
                gp_count = 0
            elif gp_count == '爆':
                gp_count = 1000
            reply_info['gp_count'] = int(gp_count)

            bp_count = reply_block.select_one('.postbp span').text
            if bp_count == '-':
                bp_count = 0
            elif bp_count == 'X':
                bp_count = 500
            reply_info['bp_count'] = int(bp_count)

            reply_info_list.append(reply_info)

        return reply_info_list
    
if __name__ == "__main__":
    crawler = BahaCrawler()
    crawler.get_article_urls_pages(60030,1,3)
    crawler.get_article_contents(60030,623773)
    



