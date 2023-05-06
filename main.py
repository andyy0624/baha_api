from typing import Optional, Union
from fastapi import FastAPI
import random as rd

from baha_utils import BahaCrawler, WebArguments, QuerryParams, WAIT_TIME, INF

app = FastAPI()  # 建立一個 Fast API application
page_engine = "selenium"  # VERY SLOW, NOT RECOMMENDED
# page_engine = "requests"
crawler = BahaCrawler(page_engine)


@app.get("/")  # 指定 api 路徑 (get方法)
def read_root():
    return {"Hello": "World"}


@app.get("/baha/get_pages_article_urls")
def get_pages_article_urls(
    bsn: Union[int, str],
    start_page: Optional[Union[int, str]] = 1,
    end_page: Optional[Union[int, str]] = None,
) -> list:
    return crawler.get_pages_article_urls(bsn, start_page, end_page)


@app.get("/baha/get_article_content")
def get_article_content(
    bsn: int,
    snA: int,
    text_only: Optional[bool] = True,
    sub_pages_limit_num: Optional[int] = INF,
    sub_pages_wait_time: Optional[Union[int, float]] = WAIT_TIME,
) -> dict:
    return crawler.get_article_content(
        WebArguments(querry_params=QuerryParams(bsn, snA)),
        text_only=text_only,
        sub_page_limit_num=sub_pages_limit_num,
        sub_page_wait_time=sub_pages_wait_time,
    )


@app.get("/baha/get_pages_article_contents")
def get_pages_article_contents(
    bsn: Union[int, str],
    text_only: Optional[bool] = True,
    start_page: Optional[Union[int, str]] = 1,
    end_page: Optional[Union[int, str]] = None,
    sub_page_limit_num: Optional[int] = INF,
    sub_page_wait_time: Optional[Union[int, float]] = WAIT_TIME,
) -> list:
    return crawler.get_pages_article_contents(
        bsn=bsn,
        text_only=text_only,
        start_page=start_page,
        end_page=end_page,
        sub_page_limit_num=sub_page_limit_num,
        sub_page_wait_time=sub_page_wait_time,
    )
