from .web_utils import UrlBuilder
from .baha_article_handler import ArticleHandler, WebRequester
from typing import Union, Optional
import random as rd

BAHA_URL = "https://forum.gamer.com.tw"
B_PAGE = "B.php"
C_PAGE = "C.php"


class BahaCrawler:
    def __init__(self, page_engine: Optional[str] = "requests") -> None:
        self._page_engine = page_engine
        self._web_requester = WebRequester("requests")

    def get_pages_article_urls(
        self,
        bsn: Union[int, str],
        start_page: Optional[Union[int, str]] = 1,
        end_page: Optional[Union[int, str]] = None,
    ) -> list:
        if end_page is None:
            end_page = start_page
        article_urls = []
        for i in range(start_page, end_page + 1):
            article_urls += self.get_page_article_urls(bsn, i)
        return article_urls

    def get_page_article_urls(
        self, bsn: Union[int, str], page: Union[int, str]
    ) -> list:
        url_builder = UrlBuilder(f"{BAHA_URL}/{B_PAGE}")
        url = url_builder(bsn=bsn, page=page)
        soup = self._web_requester(url)

        article_urls = []
        item_blocks = soup.select("table.b-list tr.b-list-item")
        if len(item_blocks) == 0:
            return [{"Error": "網頁沒有任何文章列表，你可能指向了錯誤的頁面", "URL": url}]

        for item_block in item_blocks:
            title_block = item_block.select_one(".b-list__main__title")
            article_url = f"{BAHA_URL}/{title_block.get('href')}"
            article_urls += [article_url]
        return article_urls

    def get_pages_article_contents(
        self,
        bsn: Union[int, str],
        limit_subPage: Optional[int] = 1,
        start_page: Optional[Union[int, str]] = 1,
        end_page: Optional[Union[int, str]] = None,
        wait_time: Optional[Union[int, float]] = (rd.random() * 4) + 1,
    ):
        article_urls = self.get_pages_article_urls(bsn, start_page, end_page)

        article_contents = []
        for article_url in article_urls:
            url_builder = UrlBuilder(article_url)
            base_url, param_dict = url_builder.parse_url()
            article_contents += [
                ArticleHandler(
                    bsn=param_dict["bsn"],
                    snA=param_dict["snA"],
                    page_engine=self._page_engine,
                ).get_article_contents(limit_page=limit_subPage, wait_time=wait_time)
            ]
        return article_contents
