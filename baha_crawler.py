import requests
from url_utils import UrlBuilder
from bs4 import BeautifulSoup
from typing import Union, Optional
import time
import random as rd
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36",
}

BAHA_URL = "https://forum.gamer.com.tw"
B_PAGE = "B.php"
C_PAGE = "C.php"


class BahaCrawler:
    def __init__(self) -> None:
        pass

    def get_article_urls_pages(
        self,
        bsn: Union[int, str],
        start_page: Union[int, str],
        end_page: Optional[Union[int, str]] = None,
    ) -> list:
        if end_page is None:
            end_page = start_page
        article_urls = [
            self._get_article_urls_page(bsn, i) for i in range(start_page, end_page + 1)
        ]
        return article_urls

    def get_article_contents(
        self,
        bsn: Union[int, str],
        snA: Union[int, str],
        wait_time: Optional[Union[int, float]] = (rd.random() * 4) + 1,
    ) -> dict:
        url_builder = UrlBuilder(f"{BAHA_URL}/{C_PAGE}")
        url = url_builder(bsn=bsn, snA=snA)

        r = requests.get(url, headers=HEADERS)
        if r.status_code != requests.codes.ok:
            return [{"Error": "網頁載入失敗", "URL": url}]

        soup = BeautifulSoup(r.text, features="lxml")
        a = soup.select_one("h1.c-post__header__title")
        if a is None:
            return [{"Error": "抓不到該文章標題", "URL": url}]
        article_title = a.text

        # 抓取回覆總頁數
        article_total_page = self._get_article_total_page_num(soup)
        # 爬取每一頁回覆
        reply_info_list = []
        url_builder_forPage = UrlBuilder(url)
        for page in range(article_total_page):
            crawler_url = url_builder_forPage(page=page + 1)
            reply_list = self._get_reply_info_list(crawler_url)
            reply_info_list += reply_list
            time.sleep(wait_time)

        article_info = {"title": article_title, "url": url, "reply": reply_info_list}
        return article_info

    def _get_article_urls_page(
        self, bsn: Union[int, str], page: Union[int, str]
    ) -> list:
        url_builder = UrlBuilder(f"{BAHA_URL}/{B_PAGE}")
        url = url_builder(bsn=bsn, page=page)
        r = requests.get(url, headers=HEADERS)
        if r.status_code != requests.codes.ok:
            return [{"Error": "網頁載入失敗", "URL": url}]

        article_url_list = []
        soup = BeautifulSoup(r.text, features="lxml")
        item_blocks = soup.select("table.b-list tr.b-list-item")
        if len(item_blocks) == 0:
            return [{"Error": "網頁沒有任何文章列表，你可能指向了錯誤的頁面", "URL": url}]

        for item_block in item_blocks:
            title_block = item_block.select_one(".b-list__main__title")
            article_url = f"{BAHA_URL}/{title_block.get('href')}"
            article_url_list += [article_url]
        return article_url_list

    def _get_article_total_page_num(self, soup: BeautifulSoup) -> int:
        """取得文章總頁數"""
        last_page_btn = soup.select_one(".BH-pagebtnA > a:last-of-type")
        article_total_page = int(last_page_btn.text)
        return article_total_page

    def _get_reply_info_list(self, url: str) -> list:
        """爬取回覆列表"""
        r = requests.get(url, headers=HEADERS)
        if r.status_code != requests.codes.ok:
            return [{"Error": "網頁載入失敗", "URL": url}]

        soup = BeautifulSoup(r.text, features="lxml")
        reply_blocks = soup.select('section[id^="post_"]')

        reply_info_list = []
        for block in reply_blocks:
            reply_info = {
                "floor": int(block.select_one(".floor").get("data-floor")),
                "user_name": block.select_one(".username").text,
                "user_id": block.select_one(".userid").text,
                "publish_time": datetime.strptime(
                    block.select_one(".edittime").get("data-mtime"), "%Y-%m-%d %H:%M:%S"
                ),
                "content": block.select_one(".c-article__content").text,
                "gp_count": 1000
                if block.select_one(".postgp span").text == "爆"
                else int(block.select_one(".postgp span").text)
                if block.select_one(".postgp span").text != "-"
                else 0,
                "bp_count": 500
                if block.select_one(".postbp span").text == "X"
                else int(block.select_one(".postbp span").text)
                if block.select_one(".postbp span").text != "-"
                else 0,
            }
            reply_info_list.append(reply_info)
        return reply_info_list


if __name__ == "__main__":
    crawler = BahaCrawler()
    crawler.get_article_urls_pages(60030, 1, 3)
    crawler.get_article_contents(60030, 623838)

    url = "https://forum.gamer.com.tw/C.php?bsn=60030&snA=522719"

    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, features="lxml")
    soup.select("a>p")
