from typing import Optional, Union
from fastapi import FastAPI
import random as rd

from baha_utils import BahaCrawler, BahaWebArguments, QuerryParams, WAIT_TIME, INF

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


@app.get("/baha/get_article_contents")
def get_article_contents(
    url: Optional[str],
    bsn: Optional[int],
    snA: Optional[int],
    sub_pages_limit_num: Optional[int] = INF,
    sub_pages_wait_time: Optional[Union[int, float]] = WAIT_TIME,
) -> dict:
    return crawler.get_article_contents(
        BahaWebArguments(url, QuerryParams(bsn, snA)),
        sub_pages_limit_num,
        sub_pages_wait_time,
    )


@app.get("/baha/get_pages_article_contents")
def get_pages_article_contents(
    bsn: Union[int, str],
    sub_pages_limit_num: Optional[int] = 1,
    start_page: Optional[Union[int, str]] = 1,
    end_page: Optional[Union[int, str]] = None,
    wait_time: Optional[Union[int, float]] = (rd.random() * 4) + 1,
) -> list:
    return crawler.get_pages_article_contents(
        bsn, sub_pages_limit_num, start_page, end_page, wait_time
    )
