from typing import Union, Optional, Type, Callable
from dataclasses import asdict


from .web_utils import UrlBuilder
from .article_handler import (
    ArticleHandler,
    WebRequester,
    WebArguments,
    BAHA_URL,
    B_PAGE,
    WAIT_TIME_FN,
    INF,
)


class BahaCrawler:
    def __init__(self, page_engine: Optional[str] = "requests") -> None:
        self._page_engine = page_engine

    def get_page_article_urls(self, web_args_b: WebArguments) -> list:
        url_builder = UrlBuilder(f"{BAHA_URL}/{B_PAGE}")
        url = url_builder(**asdict(web_args_b.query_params))
        soup = WebRequester("requests")(url)

        article_urls = []
        item_blocks = soup.select("table.b-list tr.b-list-item")
        if len(item_blocks) == 0:
            raise ValueError({"Error": "網頁沒有任何文章列表，你可能指向了錯誤的頁面", "URL": url})

        for item_block in item_blocks:
            title_block = item_block.select_one(".b-list__main__title")
            article_url = f"{BAHA_URL}/{title_block.get('href')}"
            article_urls += [article_url]
        return article_urls

    def get_pages_article_urls(
        self,
        web_args_b: WebArguments,
        start_page: Optional[int] = 1,
        end_page: Optional[int] = None,
    ) -> list:
        if end_page is None:
            end_page = start_page
        article_urls = []
        for page in range(start_page, end_page + 1):
            web_args_b.query_params.page = page
            article_urls += self.get_page_article_urls(web_args_b)
        return article_urls

    def get_article_content(
        self,
        web_args_c: WebArguments,
        text_only: Optional[int] = 1,
        sub_page_limit_num: Optional[int] = INF,
        sub_page_wait_time_fn: Optional[Callable] = WAIT_TIME_FN,
    ) -> dict:
        web_args_c.page_engine = self._page_engine
        return ArticleHandler(web_args_c).get_article_content(
            text_only=text_only,
            sub_page_limit_num=sub_page_limit_num,
            sub_page_wait_time_fn=sub_page_wait_time_fn,
        )

    def get_pages_article_contents(
        self,
        web_args_b: WebArguments,
        text_only: Optional[int] = 1,
        start_page: Optional[int] = 1,
        end_page: Optional[int] = None,
        sub_page_limit_num: Optional[int] = INF,
        sub_page_wait_time_fn: Optional[Callable] = WAIT_TIME_FN,
    ) -> list:
        web_args_b.page_engine = self._page_engine
        article_urls = self.get_pages_article_urls(web_args_b, start_page, end_page)

        article_contents = []
        for article_url in article_urls:
            web_args_c = WebArguments(url=article_url,page_engine=self._page_engine)
            article_contents += [
                ArticleHandler(web_args_c).get_article_content(
                    text_only=text_only,
                    sub_page_limit_num=sub_page_limit_num,
                    sub_page_wait_time_fn=sub_page_wait_time_fn,
                )
            ]
        return article_contents
