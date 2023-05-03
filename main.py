from typing import Optional, Union
from fastapi import FastAPI
import random as rd
from baha_utils import BahaCrawler
from baha_utils import ArticleHandler


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
    bsn: Union[int, str],
    snA: Union[int, str],
    limit_page: Optional[int] = float("inf"),
    wait_time: Optional[Union[int, float]] = (rd.random() * 4) + 1,
) -> dict:
    return ArticleHandler(
        bsn=bsn, snA=snA, page_engine=page_engine
    ).get_article_contents(limit_page, wait_time)


@app.get("/baha/get_pages_article_contents")
def get_pages_article_contents(
    bsn: Union[int, str],
    limit_subPage: Optional[int] = 1,
    start_page: Optional[Union[int, str]] = 1,
    end_page: Optional[Union[int, str]] = None,
    wait_time: Optional[Union[int, float]] = (rd.random() * 4) + 1,
) -> list:
    return crawler.get_pages_article_contents(
        bsn, limit_subPage, start_page, end_page, wait_time
    )
